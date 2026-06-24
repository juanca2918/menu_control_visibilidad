# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class UserVisibilityConfig(models.Model):
    _name = 'user.visibility.config'
    _description = 'Configuración de Visibilidad por Usuario'
    _rec_name = 'user_id'

    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        required=False,
        ondelete='cascade',
        index=True
    )
    menu_visibility_ids = fields.One2many(
        'user.menu.visibility',
        'config_id',
        string='Visibilidad de Menús',
        help='Configura qué menús puede ver este usuario'
    )
    field_visibility_ids = fields.One2many(
        'user.field.visibility',
        'user_id',
        string='Visibilidad de Campos',
        help='Configura qué campos puede ver este usuario en diferentes modelos'
    )
    active = fields.Boolean(string='Activo', default=True)
    
    filter_by_creator_global = fields.Boolean(
        string='📄 Solo Mis Documentos (Global)',
        default=False,
        help='Si se activa, TODOS los menús mostrarán solo documentos creados/asignados al usuario. '
             'Esta opción se aplica globalmente a todos los menús visibles del usuario.'
    )
    
    notes = fields.Text(
        string='Notas',
        help='Notas adicionales sobre la configuración de este usuario'
    )

    _sql_constraints = [
        ('user_unique', 'UNIQUE(user_id)',
         'Ya existe una configuración para este usuario')
    ]

    def copy(self, default=None):
        """
        Al duplicar:
        - Limpia user_id para que el admin seleccione el nuevo usuario.
        - Copia explícitamente todas las líneas de menú con sus configuraciones
          (visible, can_create, can_write, can_unlink, filter_by_creator).
          Si no se hace explícitamente, Odoo no replica correctamente las líneas
          porque user_id es un campo related almacenado que queda desvinculado.
        """
        default = dict(default or {})
        default['user_id'] = False
        # Al incluir menu_visibility_ids en default, Odoo usa estos valores
        # y NO intenta auto-copiar las líneas originales (evita duplicados).
        default['menu_visibility_ids'] = [
            (0, 0, {
                'menu_id': line.menu_id.id,
                'visible': line.visible,
                'can_create': line.can_create,
                'can_write': line.can_write,
                'can_unlink': line.can_unlink,
                'filter_by_creator': line.filter_by_creator,
            })
            for line in self.menu_visibility_ids
        ]
        return super().copy(default)

    @api.model
    def get_or_create_config(self, user_id):
        """
        Obtiene o crea la configuración para un usuario
        """
        config = self.search([('user_id', '=', user_id)], limit=1)
        if not config:
            config = self.create({'user_id': user_id})
        return config

    def action_configure_menus(self):
        """
        Abre la vista de configuración de menús para este usuario
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configurar Menús',
            'res_model': 'user.menu.visibility',
            'view_mode': 'list,form',
            'domain': [('user_id', '=', self.user_id.id)],
            'context': {
                'default_user_id': self.user_id.id,
                'search_default_user_id': self.user_id.id,
            },
        }

    def action_configure_fields(self):
        """
        Abre la vista de configuración de campos para este usuario
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configurar Campos',
            'res_model': 'user.field.visibility',
            'view_mode': 'list,form',
            'domain': [('user_id', '=', self.user_id.id)],
            'context': {
                'default_user_id': self.user_id.id,
                'search_default_user_id': self.user_id.id,
            },
        }

    def action_quick_menu_setup(self):
        """
        Carga TODOS los menús del sistema directamente en el formulario actual
        """
        self.ensure_one()
        
        # Validar que haya un usuario seleccionado
        if not self.user_id:
            raise UserError("⚠️ Debes seleccionar un usuario primero antes de cargar los menús.")
        
        # Obtener TODOS los menús activos del sistema sin excepción
        all_menus = self.env['ir.ui.menu'].search([
            ('active', '=', True)
        ])
        
        menus_created = 0
        menus_existing = 0
        
        # Para cada menú, crear registro de visibilidad si no existe
        for menu in all_menus:
            visibility = self.env['user.menu.visibility'].search([
                ('config_id', '=', self.id),
                ('menu_id', '=', menu.id)
            ], limit=1)
            
            if not visibility:
                self.env['user.menu.visibility'].create({
                    'config_id': self.id,
                    'menu_id': menu.id,
                    'visible': True,
                    'can_create': True,
                    'can_write': True,
                    'can_unlink': True,
                })
                menus_created += 1
            else:
                menus_existing += 1
        
        # Forzar recálculo de campos computados para TODOS los registros del usuario
        all_user_visibilities = self.env['user.menu.visibility'].search([
            ('config_id', '=', self.id)
        ])
        all_user_visibilities._compute_menu_complete_name()
        all_user_visibilities._compute_menu_path()
        
        # Forzar recomputación del campo computado menu_visibility_ids
        self.invalidate_recordset(['menu_visibility_ids'])
        
        # Mostrar mensaje de confirmación
        message = f'✅ Se cargaron {menus_created} menús nuevos. Ya existían {menus_existing} menús. Total: {len(all_user_visibilities)} menús configurados.'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Menús Cargados Exitosamente',
                'message': message,
                'type': 'success',
                'sticky': True,
            }
        }

    def action_refresh_menus(self):
        """
        Fuerza la recarga de menús para el usuario configurado
        """
        self.ensure_one()
        
        # Limpiar cache de menús
        self.env['ir.ui.menu'].clear_caches()
        
        # Enviar notificación al navegador para informar (opcional)
        try:
            if self.user_id and self.user_id.partner_id:
                self.env['bus.bus']._sendone(
                    self.user_id.partner_id,
                    'simple_notification',
                    {
                        'type': 'success',
                        'title': 'Menús Actualizados',
                        'message': f'Los menús de {self.user_id.name} han sido recargados. '
                                  'El usuario debe refrescar el navegador (F5).',
                        'sticky': False,
                    }
                )
        except Exception:
            pass
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Menús Actualizados',
                'message': f'Los menús se han recargado para {self.user_id.name}. '
                          'El usuario debe refrescar su navegador (F5) para ver los cambios.',
                'type': 'success',
                'sticky': False,
            }
        }
