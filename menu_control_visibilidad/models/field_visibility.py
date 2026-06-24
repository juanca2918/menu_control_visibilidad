# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FieldVisibility(models.Model):
    _name = 'user.field.visibility'
    _description = 'Configuración de Visibilidad de Campos por Usuario'
    _rec_name = 'field_id'

    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        required=True,
        ondelete='cascade',
        index=True
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Modelo',
        required=True,
        ondelete='cascade',
        help='Modelo donde se encuentra el campo (ej: product.product, res.partner)'
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        string='Campo',
        required=True,
        ondelete='cascade',
        domain="[('model_id', '=', model_id)]",
        help='Campo a mostrar u ocultar'
    )
    visible = fields.Boolean(
        string='Visible',
        default=True,
        help='Si está marcado, el usuario puede ver este campo'
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )

    _sql_constraints = [
        ('user_field_unique', 'UNIQUE(user_id, field_id)',
         'Ya existe una configuración para este usuario y campo')
    ]

    @api.model
    def check_field_access(self, model_name, field_name, user_id=None):
        """
        Verifica si un usuario tiene acceso a un campo específico
        """
        if not user_id:
            user_id = self.env.user.id
        
        # Los administradores siempre tienen acceso
        if self.env.user.has_group('base.group_system'):
            return True
        
        model = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
        if not model:
            return True
        
        field = self.env['ir.model.fields'].search([
            ('model_id', '=', model.id),
            ('name', '=', field_name)
        ], limit=1)
        
        if not field:
            return True
        
        visibility = self.search([
            ('user_id', '=', user_id),
            ('field_id', '=', field.id),
            ('active', '=', True)
        ], limit=1)
        
        if visibility:
            return visibility.visible
        
        # Por defecto, si no hay configuración, el campo es visible
        return True

    @api.model
    def get_hidden_fields(self, model_name, user_id=None):
        """
        Retorna la lista de nombres de campos ocultos para un usuario en un modelo
        """
        if not user_id:
            user_id = self.env.user.id
        
        # Los administradores ven todo
        if self.env.user.has_group('base.group_system'):
            return []
        
        model = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
        if not model:
            return []
        
        hidden_fields = self.search([
            ('user_id', '=', user_id),
            ('model_id', '=', model.id),
            ('visible', '=', False),
            ('active', '=', True)
        ])
        
        return hidden_fields.mapped('field_id.name')
