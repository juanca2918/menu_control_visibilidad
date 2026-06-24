# -*- coding: utf-8 -*-

from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_open_menu_visibility(self):
        """
        Abre la configuración de visibilidad de menús del usuario actual.
        Si no existe configuración, la crea automáticamente.
        """
        self.ensure_one()
        config = self.env['user.visibility.config'].search([
            ('user_id', '=', self.id),
        ], limit=1)
        if not config:
            config = self.env['user.visibility.config'].create({
                'user_id': self.id,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': f'Control de Menús — {self.name}',
            'res_model': 'user.visibility.config',
            'view_mode': 'form',
            'res_id': config.id,
            'target': 'current',
        }
