# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MenuVisibility(models.Model):
    _name = 'user.menu.visibility'
    _description = 'Configuración de Visibilidad de Menús por Usuario'
    _rec_name = 'menu_id'

    config_id = fields.Many2one(
        'user.visibility.config',
        string='Configuración',
        required=True,
        ondelete='cascade',
        index=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        related='config_id.user_id',
        store=True,
        index=True
    )
    menu_id = fields.Many2one(
        'ir.ui.menu',
        string='Menú',
        required=True,
        ondelete='cascade',
        index=True
    )
    parent_menu_id = fields.Many2one(
        'ir.ui.menu',
        string='Menú Padre',
        related='menu_id.parent_id',
        store=True,
        readonly=True
    )
    menu_sequence = fields.Integer(
        string='Secuencia',
        related='menu_id.sequence',
        store=True,
        readonly=True
    )
    menu_path = fields.Char(
        string='Ruta de Ordenamiento',
        compute='_compute_menu_path',
        store=True,
        help='Ruta jerárquica para ordenamiento'
    )
    menu_complete_name = fields.Char(
        string='Ruta del Menú',
        compute='_compute_menu_complete_name',
        store=True,
        help='Ruta completa del menú con jerarquía'
    )
    visible = fields.Boolean(
        string='Visible',
        default=True,
        help='Si está marcado, el usuario puede ver este menú'
    )
    can_create = fields.Boolean(
        string='Puede Crear',
        default=True,
        help='Permite crear nuevos registros desde este menú'
    )
    can_write = fields.Boolean(
        string='Puede Editar',
        default=True,
        help='Permite editar registros existentes desde este menú'
    )
    can_unlink = fields.Boolean(
        string='Puede Eliminar',
        default=True,
        help='Permite eliminar registros desde este menú'
    )
    filter_by_creator = fields.Boolean(
        string='Solo Mis Documentos',
        default=False,
        help='Si está marcado, el usuario solo verá los registros que él creó'
    )
    model_name = fields.Char(
        string='Modelo',
        compute='_compute_model_name',
        store=True,
        help='Modelo asociado al menú (si existe)'
    )
    action_id = fields.Integer(
        string='ID de Acción',
        compute='_compute_action_id',
        store=True,
        help='ID de la acción (ir.actions.act_window) asociada al menú'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )

    _sql_constraints = [
        ('config_menu_unique', 'UNIQUE(config_id, menu_id)',
         'Ya existe una configuración para este menú en esta configuración de usuario')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        """Override create para invalidar cache de menús"""
        records = super(MenuVisibility, self).create(vals_list)
        # Invalidar cache de menús para los usuarios afectados
        self._invalidate_menu_cache(records.mapped('user_id'))
        return records

    @api.onchange('visible')
    def _onchange_visible(self):
        """
        Actualización en tiempo real cuando se cambia la visibilidad en la interfaz
        """
        for record in self:
            if not record.menu_id or not record.user_id:
                continue
                
            # DESACTIVAR: Si desactivo un padre, desactivar visualmente los hijos
            if record.visible == False:
                child_menus = self._get_all_child_menus(record.menu_id)
                if child_menus:
                    # Buscar los registros de visibilidad de los hijos en la vista actual
                    # Esto actualizará la interfaz sin guardar aún
                    child_visibilities = self.search([
                        ('config_id', '=', record.config_id.id),
                        ('menu_id', 'in', child_menus.ids)
                    ])
                    # Actualizar valores en memoria para reflejar en la UI
                    for child in child_visibilities:
                        child.visible = False
            
            # ACTIVAR: Activar automáticamente todos los padres
            elif record.visible == True:
                parent_menus = self._get_all_parent_menus(record.menu_id)
                if parent_menus:
                    # Activar visualmente todos los padres en la interfaz
                    for parent_menu in parent_menus:
                        parent_visibility = self.search([
                            ('config_id', '=', record.config_id.id),
                            ('menu_id', '=', parent_menu.id)
                        ], limit=1)
                        
                        if parent_visibility:
                            # Actualizar en memoria para que se vea en la UI
                            parent_visibility.visible = True

    def write(self, vals):
        """Override write para invalidar cache y controlar visibilidad de submenús"""
        # Si se está cambiando la visibilidad, aplicar en cascada (solo si no estamos en cascada ya)
        if 'visible' in vals and not self.env.context.get('skip_cascade'):
            for record in self:
                if record.menu_id:
                    # DESACTIVAR: Si desactivo un padre, desactivar TODOS los hijos recursivamente
                    if vals['visible'] == False:
                        child_menus = self._get_all_child_menus(record.menu_id)
                        if child_menus:
                            child_visibilities = self.search([
                                ('config_id', '=', record.config_id.id),
                                ('menu_id', 'in', child_menus.ids)
                            ])
                            if child_visibilities:
                                # Usar contexto para evitar recursión infinita
                                child_visibilities.with_context(skip_cascade=True).write({'visible': False})
                    
                    # ACTIVAR: Si activo un hijo, ACTIVAR AUTOMÁTICAMENTE todos los padres
                    elif vals['visible'] == True:
                        # Obtener TODOS los padres (padre, abuelo, bisabuelo, etc.)
                        parent_menus = self._get_all_parent_menus(record.menu_id)
                        if parent_menus:
                            # Buscar o crear configuraciones para todos los padres
                            for parent_menu in parent_menus:
                                parent_visibility = self.search([
                                    ('config_id', '=', record.config_id.id),
                                    ('menu_id', '=', parent_menu.id)
                                ], limit=1)
                                
                                if parent_visibility:
                                    # Si existe pero está desactivado, activarlo
                                    if not parent_visibility.visible:
                                        parent_visibility.with_context(skip_cascade=True).write({'visible': True})
                                else:
                                    # Si no existe, crearlo como visible
                                    self.with_context(skip_cascade=True).create({
                                        'config_id': record.config_id.id,
                                        'menu_id': parent_menu.id,
                                        'visible': True,
                                    })
        
        result = super(MenuVisibility, self).write(vals)
        
        # IMPORTANTE: Flush para asegurar que los cambios están en la BD antes de invalidar caché
        self.flush_model()
        
        # Invalidar cache de menús para los usuarios afectados
        if 'visible' in vals:
            self._invalidate_menu_cache(self.mapped('user_id'))
        
        # Si se modificaron permisos (can_create, can_write, can_unlink), invalidar caché de vistas
        permission_fields = {'can_create', 'can_write', 'can_unlink', 'filter_by_creator'}
        if any(field in vals for field in permission_fields):
            self._invalidate_view_cache(self.mapped('user_id'))
        
        return result

    def _get_all_child_menus(self, menu):
        """
        Obtiene recursivamente todos los menús hijos (hijos, nietos, etc.)
        """
        children = self.env['ir.ui.menu'].search([('parent_id', '=', menu.id)])
        all_children = children
        for child in children:
            all_children |= self._get_all_child_menus(child)
        return all_children
    
    def _get_all_parent_menus(self, menu):
        """
        Obtiene recursivamente todos los menús padres (padre, abuelo, bisabuelo, etc.)
        """
        parents = self.env['ir.ui.menu']
        current = menu.parent_id
        while current:
            parents |= current
            current = current.parent_id
        return parents

    def unlink(self):
        """Override unlink para invalidar cache de menús"""
        users = self.mapped('user_id')
        result = super(MenuVisibility, self).unlink()
        # Invalidar cache de menús para los usuarios afectados
        self._invalidate_menu_cache(users)
        return result

    def _invalidate_menu_cache(self, users):
        """
        Invalida el cache de menús para los usuarios especificados
        """
        if not users:
            return
        
        # Limpiar cache de ir.ui.menu
        self.env['ir.ui.menu'].clear_caches()
        
        # Notificar al navegador para recargar menús (si el módulo bus está disponible)
        try:
            for user in users:
                if user.partner_id:
                    self.env['bus.bus']._sendone(
                        user.partner_id,
                        'simple_notification',
                        {
                            'type': 'info',
                            'title': 'Menús Actualizados',
                            'message': 'Los menús han sido actualizados. Refresca el navegador (F5) para ver los cambios.',
                            'sticky': False,
                        }
                    )
        except Exception:
            # Si falla la notificación, no es crítico
            pass

    @api.depends('menu_id', 'menu_id.action')
    def _compute_model_name(self):
        """
        Obtiene el modelo asociado al menú desde la acción
        """
        for record in self:
            model_name = False
            if record.menu_id and record.menu_id.action:
                action = record.menu_id.action
                # Extraer el modelo según el tipo de acción
                if hasattr(action, 'res_model'):
                    model_name = action.res_model
            record.model_name = model_name

    @api.depends('menu_id', 'menu_id.action')
    def _compute_action_id(self):
        """
        Obtiene el ID de la acción asociada al menú.
        Este campo es CLAVE para identificar unívocamente el menú en get_views(),
        ya que Odoo 18 pasa action_id en options y cada menú tiene su propia acción.
        Ej: 'Cotizaciones' y 'Órdenes de Venta' tienen DIFERENTE action_id aunque
        usen el mismo modelo sale.order.
        """
        for record in self:
            action_id = 0
            if record.menu_id and record.menu_id.action:
                action_id = record.menu_id.action.id or 0
            record.action_id = action_id

    @api.depends('menu_id', 'menu_id.name', 'menu_id.parent_id')
    def _compute_menu_complete_name(self):
        """
        Calcula el nombre completo del menú con jerarquía visual
        """
        for record in self:
            if not record.menu_id:
                record.menu_complete_name = ''
                continue
            
            menu = record.menu_id
            
            # Contar el nivel de profundidad
            level = 0
            current = menu
            while current.parent_id:
                level += 1
                current = current.parent_id
            
            # Crear indentación visual según el nivel usando caracteres Unicode más visibles
            if level == 0:
                # Menú raíz - sin indentación, icono de carpeta
                record.menu_complete_name = f"📁 {menu.name}"
            elif level == 1:
                # Primer nivel - usar línea y rama
                record.menu_complete_name = f"  ├─ {menu.name}"
            elif level == 2:
                # Segundo nivel - doble indentación
                record.menu_complete_name = f"    ├─ {menu.name}"
            elif level == 3:
                # Tercer nivel - triple indentación
                record.menu_complete_name = f"      ├─ {menu.name}"
            elif level == 4:
                # Cuarto nivel
                record.menu_complete_name = f"        ├─ {menu.name}"
            else:
                # Niveles más profundos - 2 espacios por nivel
                indent = '  ' * level
                record.menu_complete_name = f"{indent}├─ {menu.name}"

    @api.depends('menu_id', 'menu_id.parent_id', 'menu_id.sequence')
    def _compute_menu_path(self):
        """
        Calcula la ruta jerárquica para ordenamiento correcto
        Genera algo como: "010/020/030" para mantener el orden de padres → hijos
        """
        for record in self:
            if not record.menu_id:
                record.menu_path = ''
                continue
            
            # Construir la ruta desde la raíz hasta el menú actual
            path_parts = []
            current = record.menu_id
            
            while current:
                # Usar sequence con padding de 4 dígitos para ordenar correctamente
                path_parts.insert(0, f"{current.sequence:04d}")
                current = current.parent_id
            
            record.menu_path = '/'.join(path_parts)

    @api.model
    def check_menu_access(self, menu_id, user_id=None):
        """
        Verifica si un usuario tiene acceso a un menú específico
        """
        if not user_id:
            user_id = self.env.user.id
        
        # Los administradores siempre tienen acceso
        if self.env.user.has_group('base.group_system'):
            return True
        
        visibility = self.search([
            ('user_id', '=', user_id),
            ('menu_id', '=', menu_id),
            ('active', '=', True)
        ], limit=1)
        
        if visibility:
            return visibility.visible
        
        # Por defecto, si no hay configuración, el menú es visible
        return True

    @api.model
    def get_hidden_menus(self, user_id=None):
        """
        Retorna la lista de IDs de menús ocultos para un usuario
        """
        if not user_id:
            user_id = self.env.user.id
        
        # Los administradores ven todo
        if self.env.user.has_group('base.group_system'):
            return []
        
        hidden_menus = self.search([
            ('user_id', '=', user_id),
            ('visible', '=', False),
            ('active', '=', True)
        ])
        
        return hidden_menus.mapped('menu_id').ids

    @api.model
    def check_operation_allowed(self, model_name, operation, user_id=None, menu_id=None):
        """
        Verifica si un usuario puede realizar una operación (create/write/unlink) en un modelo
        
        Args:
            model_name: Nombre del modelo (ej: 'res.partner')
            operation: 'create', 'write' o 'unlink'
            user_id: ID del usuario (por defecto el usuario actual)
            menu_id: ID del menú desde el que se accede (opcional)
        
        Returns:
            Boolean: True si la operación está permitida, False si está bloqueada
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        if not user_id:
            user_id = self.env.user.id
        
        _logger.debug(f"🔐 check_operation_allowed: modelo={model_name}, operación={operation}, usuario_id={user_id}, menu_id={menu_id}")
        
        # Los administradores pueden hacer todo
        if self.env.user.has_group('base.group_system'):
            return True
        
        # Verificar si el usuario tiene configuración activa
        user_config = self.env['user.visibility.config'].search([
            ('user_id', '=', user_id),
            ('active', '=', True)
        ], limit=1)
        
        # Si NO tiene configuración activa, permitir todo (comportamiento por defecto)
        if not user_config:
            return True
        
        # Mapeo de operación a campo
        field_map = {
            'create': 'can_create',
            'write': 'can_write',
            'unlink': 'can_unlink',
        }
        
        field_name = field_map.get(operation)
        if not field_name:
            return True
        
        _logger.debug(f"   Buscando configuraciones para modelo={model_name}, campo={field_name}")
        
        # Buscar configuraciones para este modelo y usuario
        domain = [
            ('user_id', '=', user_id),
            ('model_name', '=', model_name),
            ('visible', '=', True),  # Solo menús visibles
            ('active', '=', True),
        ]
        
        # Si tenemos menu_id, filtrar SOLO por ese menú específico
        if menu_id:
            domain.append(('menu_id', '=', menu_id))
            _logger.debug(f"   🎯 Filtrando por menú específico: {menu_id}")
        
        menu_configs = self.search(domain)
        
        _logger.debug(f"   Configuraciones encontradas: {len(menu_configs)}")
        for config in menu_configs:
            _logger.debug(f"      - Menú: {config.menu_id.name}, {field_name}={config[field_name]}")
        
        # Si NO hay configuración para este modelo, permitir (no está controlado)
        if not menu_configs:
            return True
        
        # LÓGICA según si tenemos menu_id o no
        if menu_id:
            # Si tenemos menu_id específico: verificar SOLO ESA configuración
            for config in menu_configs:
                if config[field_name]:
                    _logger.debug(f"   ✅ Menú '{config.menu_id.name}' (ID:{menu_id}) permite {operation}")
                    return True
            _logger.debug(f"   ❌ El menú específico (ID:{menu_id}) NO permite {operation}, DENEGAR")
            return False
        else:
            # Sin menu_id: no sabemos desde qué menú viene el usuario.
            # La restricción es POR MENÚ — si no podemos identificarlo,
            # NO aplicamos restricciones (política de mínimo impacto).
            # Esto evita que una config de Contactos bloquee el botón Crear
            # en Clientes (Ventas) o Proveedores (Compras) que comparten modelo.
            _logger.debug(f"   ⚠️ Sin menu_id → permitir por defecto (no se puede identificar menú)")
            return True

    def _invalidate_view_cache(self, users):
        """
        Invalida el caché de vistas para los usuarios especificados
        Esto fuerza a Odoo a recalcular las vistas con los nuevos permisos
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        if not users:
            return
        
        _logger.debug(f"🔄 Invalidando caché de vistas para usuarios: {users.mapped('name')}")
        
        # Limpiar caché de métodos relacionados con vistas
        try:
            # Limpiar caché de ir.ui.view
            self.env['ir.ui.view'].clear_caches()
            _logger.debug(f"   ✅ Caché de ir.ui.view limpiado")
            
            # Limpiar caché del registry - esto invalida get_views() en todos los modelos
            # Es más agresivo pero necesario para que los cambios se apliquen
            self.env.registry.clear_caches()
            _logger.debug(f"   ✅ Caché de registry limpiado")
            
            # Notificar a los usuarios para que refresquen
            for user in users:
                if user.partner_id:
                    try:
                        self.env['bus.bus']._sendone(
                            user.partner_id,
                            'simple_notification',
                            {
                                'type': 'info',
                                'title': '✅ Permisos Actualizados',
                                'message': 'Refresca la página (F5) para que los cambios tomen efecto.',
                                'sticky': True,
                            }
                        )
                        _logger.debug(f"   📢 Notificación enviada a {user.name}")
                    except Exception as e:
                        _logger.warning(f"   ⚠️  No se pudo enviar notificación a {user.name}: {e}")
        except Exception as e:
            _logger.error(f"   ❌ Error invalidando caché: {e}")
            import traceback
            _logger.error(traceback.format_exc())

