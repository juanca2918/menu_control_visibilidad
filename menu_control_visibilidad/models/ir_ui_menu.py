# -*- coding: utf-8 -*-

from odoo import models, api


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _get_all_parent_ids(self, menu_ids):
        """
        Obtiene todos los IDs de menús padres (incluyendo abuelos, bisabuelos, etc.)
        para los menús dados. Esto es necesario para que Odoo pueda construir
        la jerarquía correctamente.
        """
        parent_ids = set()
        menus = self.browse(menu_ids)
        
        for menu in menus:
            current = menu.parent_id
            while current:
                parent_ids.add(current.id)
                current = current.parent_id
        
        return parent_ids

    @api.model
    def _visible_menu_ids(self, debug=False):
        """
        Override para filtrar menús según configuración de visibilidad por usuario
        """
        # Obtener menús visibles por defecto (incluye filtrado por grupos y permisos)
        visible_ids = super()._visible_menu_ids(debug=debug)
        
        # Si es administrador del sistema, mostrar todos
        if self.env.user.has_group('base.group_system'):
            return visible_ids
        
        # Verificar si el usuario tiene configuración activa
        user_config = self.env['user.visibility.config'].search([
            ('user_id', '=', self.env.user.id),
            ('active', '=', True)
        ], limit=1)
        
        # Si NO tiene configuración activa, mostrar todos los menús por defecto
        if not user_config:
            return visible_ids
        
        # Si tiene configuración, obtener menús visibles
        visible_menus = self.env['user.menu.visibility'].search([
            ('user_id', '=', self.env.user.id),
            ('visible', '=', True),
            ('active', '=', True)
        ])
        
        # Si tiene configuración pero sin menús visibles, retornar vacío (no mostrar nada)
        if not visible_menus:
            return set()
        
        # Obtener IDs de menús permitidos
        allowed_menu_ids = set(visible_menus.mapped('menu_id').ids)
        
        # CRÍTICO: Agregar TODOS los padres de los menús visibles
        # Sin esto, Odoo no puede construir la jerarquía y muestra pantalla en blanco
        parent_ids = self._get_all_parent_ids(allowed_menu_ids)
        allowed_menu_ids = allowed_menu_ids | parent_ids
        
        # Retornar intersección: solo menús que están TANTO en visible_ids COMO en allowed_menu_ids
        return visible_ids & allowed_menu_ids
