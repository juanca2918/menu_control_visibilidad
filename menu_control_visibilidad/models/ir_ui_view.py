# -*- coding: utf-8 -*-

from odoo import models, api


class IrModel(models.Model):
    _inherit = 'ir.model'

    @api.model
    def get_fields_visibility(self, model_name):
        """
        Retorna información sobre qué campos están ocultos para el usuario actual
        """
        if self.env.user.has_group('base.group_system'):
            return {}
        
        hidden_fields = self.env['user.field.visibility'].search([
            ('user_id', '=', self.env.user.id),
            ('visible', '=', False),
            ('active', '=', True)
        ])
        
        result = {}
        for field_config in hidden_fields:
            if field_config.model_id.model == model_name:
                result[field_config.field_id.name] = False
        
        return result


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def _apply_field_visibility(self, result, model):
        """
        Aplica la configuración de visibilidad de campos a las vistas
        """
        # Si es administrador, no modificar
        if self.env.user.has_group('base.group_system'):
            return result
        
        # Obtener campos ocultos para el modelo
        hidden_fields_config = self.env['user.field.visibility'].search([
            ('user_id', '=', self.env.user.id),
            ('visible', '=', False),
            ('active', '=', True)
        ])
        
        # Filtrar por modelo actual
        model_obj = self.env['ir.model'].search([('model', '=', model)], limit=1)
        if not model_obj:
            return result
        
        hidden_fields = []
        for config in hidden_fields_config:
            if config.model_id.id == model_obj.id:
                hidden_fields.append(config.field_id.name)
        
        if not hidden_fields:
            return result
        
        # Modificar la arquitectura para ocultar campos
        if 'arch' in result:
            import lxml.etree as etree
            arch = etree.fromstring(result['arch'])
            
            # Buscar y ocultar campos
            for field_name in hidden_fields:
                for field in arch.xpath(f"//field[@name='{field_name}']"):
                    # Agregar atributo invisible
                    field.set('invisible', '1')
                    # También agregar clase para ocultar con CSS
                    current_class = field.get('class', '')
                    field.set('class', f"{current_class} o_hidden".strip())
            
            result['arch'] = etree.tostring(arch, encoding='unicode')
        
        return result

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """
        Override para aplicar visibilidad de campos
        """
        result = super().get_view(view_id=view_id, view_type=view_type, **options)
        
        # Aplicar visibilidad de campos si hay un modelo
        if result.get('model'):
            result = self._apply_field_visibility(result, result['model'])
        
        return result
