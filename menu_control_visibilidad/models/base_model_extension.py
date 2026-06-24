# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import AccessError, UserError
import logging

_logger = logging.getLogger(__name__)


class BaseModelExtension(models.AbstractModel):
    """
    Extensión del modelo base para aplicar restricciones de permisos personalizadas
    """
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        """
        Override get_views para modificar las vistas dinámicamente según permisos personalizados
        """
        from lxml import etree
        
        # ────────────────────────────────────────────────────────────────────
        # LÓGICA DE RESTRICCIÓN BASADA EN TIPO DE USUARIO NATIVO DE ODOO
        # ────────────────────────────────────────────────────────────────────
        # • Administrador del sistema (base.group_system): sale aquí arriba sin
        #   ninguna restricción — ve todos los botones y formularios.
        # • Tipo Usuario (internal user, sin base.group_system): si tiene una
        #   configuración activa en este módulo, se le aplican las restricciones
        #   de CRUD (create/write/delete en root_node) y se le ocultan TODOS los
        #   botones de acción del <header> (Confirmar, Pagar, Restablecer,
        #   Nota de Crédito, Cancelar, Validar, etc.) excepto los de impresión.
        # ────────────────────────────────────────────────────────────────────
        # Si es administrador, no aplicar restricciones
        if self.env.user.has_group('base.group_system'):
            return super(BaseModelExtension, self).get_views(views, options=options)
        
        # ── BLOQUEO DE FICHAS DE PRODUCTOS ────────────────────────────────────
        # get_views() SOLO se llama cuando el usuario navega directamente a una
        # vista. NO se llama cuando Odoo carga datos relacionados (product_id en
        # líneas de factura, etc.). Por eso es el lugar correcto para bloquear.
        #
        # IMPORTANTE: Odoo 18 carga list+form juntos en la carga inicial del menú.
        # Solo bloqueamos cuando únicamente se pide el form (el usuario hizo click
        # sobre un registro). Si viene acompañado de 'list' o 'tree' es la carga
        # inicial del menú y debemos dejar pasar para que la lista sea visible.
        if self._name in ['product.product', 'product.template']:
            view_types = [vt for _vid, vt in views]
            if 'form' in view_types and len(view_types) == 1:
                # Los managers de inventario pueden abrir fichas de producto libremente.
                # El resto de usuarios con config activa solo pueden ver la lista.
                is_stock_manager = self.env.user.has_group('stock.group_stock_manager')
                if not is_stock_manager:
                    # Administradores de Inventario (stock.group_stock_manager)
                    # o de Productos (product.group_product_manager con 'manager')
                    # SIEMPRE pueden abrir fichas de producto.
                    _groups_xmlids = self.env.user.groups_id.get_external_id()
                    is_inventory_manager = any(
                        (xmlid or '').startswith(('stock.', 'product.'))
                        and ('manager' in xmlid or 'admin' in xmlid)
                        for xmlid in _groups_xmlids.values()
                    )
                    if not is_inventory_manager:
                        has_config = self.env['user.menu.visibility'].search_count([
                            ('user_id', '=', self.env.user.id),
                            ('active', '=', True),
                        ], limit=1)
                        if has_config:
                            raise UserError(
                                _('❌ ACCESO RESTRINGIDO A PRODUCTOS\n\n'
                                  'No tienes permiso para abrir las fichas de productos.\n'
                                  'Puedes visualizarlos en las listas pero no acceder a los detalles.')
                            )
        
        result = super(BaseModelExtension, self).get_views(views, options=options)
        
        model_name = self._name
        menu_id = None
        action_id = None

        # Extraer action_id y menu_id de todas las fuentes disponibles
        if options:
            action_id = options.get('action_id')
        params = self.env.context.get('params', {})
        ctx_menu_id = (
            params.get('menu_id')
            or self.env.context.get('menu_id')
            or self.env.context.get('active_menu_id')
        )
        if not action_id:
            action_id = (
                params.get('action')
                or self.env.context.get('action_id')
                or self.env.context.get('action')
            )

        _logger.debug(f"🎨 get_views: modelo={model_name}, action_id={action_id}, ctx_menu_id={ctx_menu_id}")

        # ── Método A: params.menu_id (MÁS DIRECTO) ────────────────────────────
        # ctx_menu_id es el ID exacto del menú que el usuario clickeó.
        # Solo lo usamos si hay una config activa para ese menú concreto.
        if ctx_menu_id:
            cfg = self.env['user.menu.visibility'].search([
                ('user_id', '=', self.env.user.id),
                ('menu_id', '=', ctx_menu_id),
                ('active', '=', True),
            ], limit=1)
            if cfg:
                menu_id = ctx_menu_id
                _logger.debug(f"   ✅ menu_id={menu_id} ('{cfg.menu_id.name}') via ctx_menu_id")

        # ── Método B: action_id de options, cruzado con ctx_menu_id ───────────
        # Odoo 18 pasa action_id en options. Si ya tenemos ctx_menu_id, lo usamos
        # para desambiguar entre menús que comparten la misma acción (Contactos,
        # Clientes Ventas y Proveedores comparten base.action_partner_form).
        if not menu_id and action_id:
            # Buscar TODOS los registros del usuario con ese action_id
            configs = self.env['user.menu.visibility'].search([
                ('user_id', '=', self.env.user.id),
                ('action_id', '=', action_id),
                ('active', '=', True),
            ])
            if configs:
                if len(configs) == 1:
                    # Solo una config → usarla directamente
                    menu_id = configs[0].menu_id.id
                    _logger.debug(f"   ✅ menu_id={menu_id} ('{configs[0].menu_id.name}') via action_id único")
                else:
                    # Múltiples configs con el mismo action_id (menús compartidos).
                    # Intentar desambiguar con ctx_menu_id si está disponible.
                    if ctx_menu_id:
                        match = configs.filtered(lambda c: c.menu_id.id == ctx_menu_id)
                        if match:
                            menu_id = ctx_menu_id
                            _logger.debug(f"   ✅ menu_id={menu_id} desambiguado via ctx_menu_id entre {len(configs)} configs")
                        else:
                            # ctx_menu_id no tiene config propia → menú sin restricción
                            _logger.debug(
                                f"   ℹ️ ctx_menu_id={ctx_menu_id} no tiene config propia "
                                f"(acción compartida) → permisos por defecto"
                            )
                    else:
                        _logger.debug(
                            f"   ⚠️ {len(configs)} configs para action_id={action_id} sin ctx_menu_id "
                            f"→ política permisiva"
                        )
        
        if not menu_id:
            _logger.debug(f"   ⚠️ menu_id no detectado para modelo={model_name}, action_id={action_id}. "
                           f"Contexto: {dict(self.env.context)}")
        
        # Verificar permisos personalizados PASANDO EL MENU_ID
        menu_visibility = self.env['user.menu.visibility']
        can_create = menu_visibility.check_operation_allowed(model_name, 'create', self.env.user.id, menu_id)
        can_write = menu_visibility.check_operation_allowed(model_name, 'write', self.env.user.id, menu_id)
        can_unlink = menu_visibility.check_operation_allowed(model_name, 'unlink', self.env.user.id, menu_id)
        
        _logger.debug(f"   Permisos: crear={can_create}, editar={can_write}, eliminar={can_unlink}")
        
        # Detectar si el usuario es manager/administrador nativo del módulo del modelo.
        # En Odoo los grupos de administrador tienen 'manager' o 'admin' en su XML ID:
        #   purchase.group_purchase_manager, account.group_account_manager, etc.
        # Los managers SIEMPRE ven los botones de acción del header aunque tengan
        # configuración activa en este módulo. Solo los 'tipo usuario' los pierden.
        #
        # CASO ESPECIAL: modelos cuyo prefijo no coincide con ningún módulo de negocio
        # (res.partner → 'res', mail.message → 'mail'). Para estos se amplía la búsqueda
        # a todos los grupos manager/admin del usuario, independientemente del prefijo.
        _model_module = self._name.split('.')[0]
        _groups_xmlids = list(self.env.user.groups_id.get_external_id().values())
        _GENERIC_MODULES = frozenset({'res', 'base', 'mail', 'ir'})
        if _model_module in _GENERIC_MODULES:
            # Para modelos genéricos: basta con ser manager en CUALQUIER módulo de negocio
            is_native_module_manager = any(
                (xmlid or '') and ('manager' in xmlid or 'admin' in xmlid)
                for xmlid in _groups_xmlids
            )
        else:
            is_native_module_manager = any(
                (xmlid or '').startswith(f'{_model_module}.') and (
                    'manager' in xmlid or 'admin' in xmlid
                )
                for xmlid in _groups_xmlids
            )
        
        # Verificar si el usuario tiene configuración activa (para restricción de botones)
        has_active_config = bool(self.env['user.visibility.config'].search_count([
            ('user_id', '=', self.env.user.id),
            ('active', '=', True),
        ]))
        
        # Modificar las vistas según permisos - MODIFICAR EL XML ARCH DIRECTAMENTE
        _logger.debug(f"   📋 Tipos de vista en result: {list(result.get('views', {}).keys())}")
        
        # Verificar permiso nativo de Odoo: "Creación de productos"
        # Grupo product.group_product_manager → checkbox "Creación de productos" en el usuario.
        # Si NO lo tiene, bloqueamos no_create/no_quick_create en todos los campos
        # product_id/product_tmpl_id de cualquier formulario (facturas, compras, ventas, etc.)
        can_create_products = self.env.user.has_group('product.group_product_manager')
        
        for view_type in result.get('views', {}):
            view_data = result['views'].get(view_type, {})
            _logger.debug(f"   🔧 Procesando vista {view_type}, tiene arch: {'arch' in view_data}")
            
            if not view_data or 'arch' not in view_data:
                _logger.debug(f"   ⏭️  Saltando vista {view_type} (sin arch)")
                continue
            
            try:
                import ast, json as _json
                # Parsear el XML
                arch_tree = etree.fromstring(view_data['arch'])
                root_node = arch_tree
                modified = False
                
                # ── BLOQUEAR CREACIÓN DE PRODUCTOS EN CAMPOS MANY2ONE ─────────────
                # Refuerza el permiso nativo "Creación de productos" en aquellos
                # formularios donde Odoo no lo aplica automáticamente.
                if not can_create_products:
                    _PRODUCT_FIELD_NAMES = {'product_id', 'product_tmpl_id', 'product_template_id'}
                    for fld in arch_tree.xpath('//field[@name]'):
                        if fld.get('name') in _PRODUCT_FIELD_NAMES:
                            opts_raw = (fld.get('options') or '{}').strip()
                            try:
                                opts = ast.literal_eval(opts_raw) if opts_raw else {}
                                if not isinstance(opts, dict):
                                    opts = {}
                            except Exception:
                                opts = {}
                            if not opts.get('no_create') or not opts.get('no_quick_create'):
                                opts['no_create'] = True
                                opts['no_quick_create'] = True
                                fld.set('options', _json.dumps(opts))
                                _logger.debug(
                                    f"   🚫 no_create añadido a {fld.get('name')} "
                                    f"en vista {view_type} de {model_name}"
                                )
                                modified = True

                # Modificar atributos según el tipo de vista
                if view_type in ['list', 'tree']:
                    if not can_create:
                        if root_node.get('create') != 'false':
                            root_node.set('create', 'false')
                            _logger.debug(f"   ❌ Deshabilitando creación en vista {view_type} (arch)")
                            modified = True
                        # También deshabilitar importación (botón "Subir")
                        if root_node.get('import') != 'false':
                            root_node.set('import', 'false')
                            _logger.debug(f"   ❌ Deshabilitando importación en vista {view_type} (arch)")
                            modified = True
                    if not can_unlink and root_node.get('delete') != 'false':
                        root_node.set('delete', 'false')
                        _logger.debug(f"   ❌ Deshabilitando eliminación en vista {view_type} (arch)")
                        modified = True
                
                # BLOQUEO ESPECIAL PARA PRODUCTOS: No permitir abrir fichas
                # Solo para usuarios que NO son managers de inventario.
                if model_name in ['product.product', 'product.template'] and view_type in ['list', 'tree']:
                    _is_stock_mgr = self.env.user.has_group('stock.group_stock_manager')
                    if not _is_stock_mgr and root_node.get('open') != '0':
                        root_node.set('open', '0')
                        _logger.debug(f"   🚫 Bloqueando apertura de productos en vista {view_type}")
                        modified = True
                        
                elif view_type == 'form':
                    if not can_write and root_node.get('edit') != 'false':
                        root_node.set('edit', 'false')
                        _logger.debug(f"   ❌ Deshabilitando edición en vista {view_type} (arch)")
                        modified = True
                    if not can_create:
                        if root_node.get('create') != 'false':
                            root_node.set('create', 'false')
                            _logger.debug(f"   ❌ Deshabilitando creación en vista {view_type} (arch)")
                            modified = True
                        # También deshabilitar el botón "Duplicar"
                        if root_node.get('duplicate') != 'false':
                            root_node.set('duplicate', 'false')
                            _logger.debug(f"   ❌ Deshabilitando duplicación en vista {view_type} (arch)")
                            modified = True
                    if not can_unlink and root_node.get('delete') != 'false':
                        root_node.set('delete', 'false')
                        _logger.debug(f"   ❌ Deshabilitando eliminación en vista {view_type} (arch)")
                        modified = True

                    # PEDIDOS DE VENTA CONFIRMADOS: tipo usuario no puede editar
                    # BUG ANTERIOR: comprobábamos `not fld.get('readonly')` antes
                    # de setear, pero el campo `order_line` nativo de Odoo 18 ya tiene
                    # readonly="state == 'cancel' or locked" → ese string es truthy →
                    # el guard `not fld.get('readonly')` devolvía False y saltábamos
                    # el campo sin tocar. SOLUCIÓN: SIEMPRE combinamos con OR.
                    if (model_name == 'sale.order'
                            and has_active_config
                            and not is_native_module_manager):
                        _LOCK_FIELDS = (
                            'order_line', 'partner_id', 'validity_date',
                            'date_order', 'client_order_ref', 'payment_term_id',
                            'fiscal_position_id', 'user_id', 'team_id',
                            'pricelist_id', 'currency_id',
                        )
                        _LOCK_EXPR = "state in ('sale', 'done')"
                        for fld in arch_tree.xpath('//field[@name]'):
                            if fld.get('name') in _LOCK_FIELDS:
                                existing = fld.get('readonly', '').strip()
                                if existing and existing not in ('False', '0', 'false'):
                                    # Combinar con expresión nativa para no romperla
                                    fld.set('readonly', f"({existing}) or ({_LOCK_EXPR})")
                                else:
                                    fld.set('readonly', _LOCK_EXPR)
                                modified = True
                        _logger.debug(
                            f"   🔒 sale.order: campos clave readonly en estados confirmados"
                        )

                    # OCULTAR BOTONES DE ACCIÓN DEL HEADER
                    # ─────────────────────────────────────────────────────────
                    # Regla para tipo usuario (no manager nativo) con config activa:
                    #
                    #  ✅ Print/Imprimir              → siempre visibles en todos los modelos
                    #  ✅ Confirmar/Validar/Aprobar   → visibles si can_create=True
                    #                                   EXCEPTO en modelos de flujo interno
                    #                                   (entregas, recepciones, stock.picking)
                    #                                   donde el tipo usuario nunca debe validar.
                    #  ❌ Todo lo demás               → siempre ocultos
                    #
                    # MODELOS DE FLUJO INTERNO: el tipo usuario nunca controla
                    # estos documentos aunque tenga can_create=True en su menú.
                    # Son creados automáticamente por el sistema (p.ej. la entrega
                    # se genera al confirmar la cotización). El tipo usuario solo
                    # debería revisarlos, no avanzar su estado.
                    _NO_CONFIRM_MODELS = frozenset({
                        'stock.picking',      # Entregas y recepciones
                        'stock.move',         # Movimientos de stock
                        'mrp.production',     # Órdenes de fabricación
                        'mrp.workorder',      # Órdenes de trabajo
                    })
                    if has_active_config and not is_native_module_manager:
                        PRINT_KEYWORDS = ('print', 'imprimir', 'report')
                        # Botones de confirmación/avance de flujo — no aplican
                        # a modelos de flujo interno (_NO_CONFIRM_MODELS)
                        CONFIRM_NAMES = frozenset({
                            'button_confirm', 'action_confirm',
                            'button_validate', 'action_validate',
                            'action_quotation_send',
                        })
                        CONFIRM_KEYWORDS = (
                            'confirm', 'confirmar',
                            'validate', 'validar',
                            'approve', 'aprobar',
                        )
                        for header in arch_tree.xpath('//header'):
                            for btn in header.findall('button'):
                                if btn.get('invisible') == 'True':
                                    continue
                                btn_name = (btn.get('name') or '').lower()
                                btn_string = (btn.get('string') or '').lower()

                                is_print = any(
                                    kw in btn_name or kw in btn_string
                                    for kw in PRINT_KEYWORDS
                                )
                                if is_print:
                                    continue

                                # En modelos de flujo interno ocultar TODOS
                                # los botones de acción (sin excepción confirm)
                                if model_name in _NO_CONFIRM_MODELS:
                                    btn.set('invisible', 'True')
                                    _logger.debug(
                                        f"   🔒 [{model_name}] Ocultando botón flujo interno "
                                        f"'{btn.get('name', btn.get('string', '?'))}'"
                                    )
                                    modified = True
                                    continue

                                is_confirm = (
                                    btn_name in CONFIRM_NAMES
                                    or any(
                                        kw in btn_name or kw in btn_string
                                        for kw in CONFIRM_KEYWORDS
                                    )
                                )
                                # Visible solo si es confirm-type Y el usuario puede crear
                                should_hide = not (is_confirm and can_create)
                                if should_hide:
                                    btn.set('invisible', 'True')
                                    _logger.debug(
                                        f"   🔒 Ocultando botón '{btn.get('name', btn.get('string', '?'))}' "
                                        f"en header de {model_name}"
                                    )
                                    modified = True
                
                # Si se modificó, actualizar el arch
                if modified:
                    new_arch = etree.tostring(arch_tree, encoding='unicode')
                    view_data['arch'] = new_arch
                    _logger.debug(f"   ✅ Vista {view_type} modificada. Arch inicio: {new_arch[:300]}...")
                    
            except Exception as e:
                _logger.error(f"   ❌ Error modificando vista {view_type}: {e}")
                import traceback
                _logger.error(traceback.format_exc())
        
        return result

    def check_access_rights(self, operation, raise_exception=True):
        """
        Override check_access_rights para integrar permisos personalizados
        Este método controla si los botones aparecen en la UI
        """
        # Llamar al método original primero
        result = super(BaseModelExtension, self).check_access_rights(operation, raise_exception=False)
        
        _logger.debug(f"🔍 check_access_rights: modelo={self._name}, operación={operation}, usuario={self.env.user.name}, resultado_original={result}")
        
        # Si el método original ya negó el acceso, respetarlo
        if not result:
            _logger.debug(f"   ❌ Permiso denegado por Odoo original")
            if raise_exception:
                raise AccessError(_('No tiene permisos para realizar esta operación.'))
            return False
        
        # Ahora verificar nuestros permisos personalizados
        custom_allowed = self._check_custom_permission(operation)
        _logger.debug(f"   🔐 Permiso personalizado: {custom_allowed}")
        
        if not custom_allowed:
            _logger.debug(f"   ❌ DENEGADO por permisos personalizados")
            if raise_exception:
                operation_names = {
                    'read': 'VER',
                    'create': 'CREAR',
                    'write': 'EDITAR',
                    'unlink': 'ELIMINAR'
                }
                raise AccessError(
                    _('❌ PERMISO DENEGADO: No puede %s registros en "%s". '
                      'Contacte al administrador para solicitar este permiso.') % 
                    (operation_names.get(operation, operation.upper()), self._description)
                )
            return False
        
        _logger.debug(f"   ✅ Permiso concedido")
        return True

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create para verificar permisos personalizados
        NOTA: check_access_rights ya se ejecutó automáticamente antes de llegar aquí
        """
        return super(BaseModelExtension, self).create(vals_list)

    def write(self, vals):
        """
        Override write para verificar permisos personalizados.
        NOTA: La protección contra editar pedidos confirmados se hace en la UI
        mediante readonly en el arch (get_views), NO aqui.
        Motivo: action_confirm() hace múltiples writes ORM sobre el mismo
        sale.order (state-change + computes + triggers). Un guard server-side
        en write() bloquearía los writes del sistema posteriores al cambio de
        estado, impidiendo confirmar el pedido.
        """
        return super(BaseModelExtension, self).write(vals)

    def unlink(self):
        """
        Override unlink para verificar permisos personalizados
        NOTA: check_access_rights ya se ejecutó automáticamente antes de llegar aquí
        """
        return super(BaseModelExtension, self).unlink()

    def _check_custom_permission(self, operation):
        """
        Verifica si el usuario actual tiene permiso para realizar la operación
        
        Args:
            operation: 'create', 'write' o 'unlink'
            
        Returns:
            Boolean: True si tiene permiso, False si no
        """
        # Los administradores siempre tienen todos los permisos
        if self.env.user.has_group('base.group_system'):
            return True
        
        # Verificar si hay configuración de visibilidad de menú para este modelo
        model_name = self._name
        
        # Usar el método del modelo user.menu.visibility
        if 'user.menu.visibility' in self.env:
            return self.env['user.menu.visibility'].check_operation_allowed(
                model_name, 
                operation,
                self.env.user.id
            )
        
        # Si no existe el modelo de configuración, permitir por defecto
        return True

    @api.model
    def web_search_read(self, domain=None, specification=None, offset=0, limit=None, order=None, count_limit=None):
        """
        Override web_search_read para aplicar filtros personalizados (ej: solo mis documentos)
        """
        # Si es administrador, no aplicar filtros
        if self.env.user.has_group('base.group_system'):
            return super(BaseModelExtension, self).web_search_read(domain, specification, offset, limit, order, count_limit)

        # Los productos son catálogo compartido — nunca aplicar "Solo Mis Documentos".
        # Aplicarlo filtraría por create_uid y mostraría solo los productos que
        # el usuario creó (generalmente 0 ó 1), rompiendo:
        #   • La lista de productos en Ventas / Compras / Inventario.
        #   • El diálogo "Ver más" al buscar productos en líneas de documento.
        if self._name in ('product.product', 'product.template'):
            return super(BaseModelExtension, self).web_search_read(domain, specification, offset, limit, order, count_limit)

        # Verificar si hay filtro por creador activo (global o individual)
        model_name = self._name
        menu_id = self.env.context.get('params', {}).get('menu_id') or self.env.context.get('menu_id') or self.env.context.get('active_menu_id')

        # ── REPORTES DE ANÁLISIS: filtro forzado siempre ────────────────────
        # Estos modelos son vistas SQL de análisis que SIEMPRE deben mostrar
        # solo los registros propios del usuario, sin depender del checkbox
        # "Solo Mis Documentos". Retornamos directamente con el filtro aplicado.
        _ANALYSIS_REPORTS = {
            'sale.report':             'user_id',
            'account.invoice.report':  'invoice_user_id',
            'purchase.report':         'user_id',
        }
        if model_name in _ANALYSIS_REPORTS:
            has_config = self.env['user.menu.visibility'].search_count([
                ('user_id', '=', self.env.user.id),
                ('active', '=', True),
            ], limit=1)
            if has_config:
                user_field = _ANALYSIS_REPORTS[model_name]
                domain = list(domain or [])
                domain.append((user_field, '=', self.env.user.id))
                _logger.debug(
                    f"📊 Reporte análisis {model_name}: aplicando filtro "
                    f"'{user_field}' para usuario {self.env.user.name}"
                )
            return super(BaseModelExtension, self).web_search_read(
                domain, specification, offset, limit, order, count_limit
            )

        apply_filter = False
        filter_source = None

        if 'user.menu.visibility' in self.env:
            # PRIMERO: Verificar si hay filtro GLOBAL activo
            user_config = self.env['user.visibility.config'].search([
                ('user_id', '=', self.env.user.id),
                ('active', '=', True),
                ('filter_by_creator_global', '=', True)
            ], limit=1)
            
            if user_config and user_config.filter_by_creator_global:
                apply_filter = True
                filter_source = 'global'
                _logger.debug(f"📄 Filtro GLOBAL activado para usuario {self.env.user.name}")
            
            # SEGUNDO: Si no hay filtro global, verificar filtro INDIVIDUAL del menú
            if not apply_filter:
                menu_visibility = self.env['user.menu.visibility']
                
                # Buscar configuración para este modelo y usuario
                config_domain = [
                    ('user_id', '=', self.env.user.id),
                    ('model_name', '=', model_name),
                    ('visible', '=', True),
                    ('active', '=', True),
                    ('filter_by_creator', '=', True)  # Solo si el filtro está activo
                ]
                
                if menu_id:
                    config_domain.append(('menu_id', '=', menu_id))
                
                menu_config = menu_visibility.search(config_domain, limit=1)
                
                if menu_config and menu_config.filter_by_creator:
                    apply_filter = True
                    filter_source = f'menú {menu_config.menu_id.name}'
                    _logger.debug(f"📄 Filtro INDIVIDUAL activado para menú '{menu_config.menu_id.name}'")
            
            # Aplicar el filtro si está activo (global o individual)
            if apply_filter:
                _logger.debug(f"📄 Aplicando filtro 'Solo Mis Documentos' ({filter_source}) para {model_name}, usuario {self.env.user.name}")
                # Agregar filtro por usuario al dominio
                domain = domain or []
                domain = list(domain) if domain else []
                
                # Intentar determinar el campo correcto según el modelo
                user_field = None
                
                # Mapeo de modelos conocidos con su campo de usuario
                model_user_fields = {
                    'sale.order': 'user_id',
                    'sale.order.line': 'order_id.user_id',
                    'account.move': 'invoice_user_id',
                    'account.move.line': 'move_id.invoice_user_id',
                    'purchase.order': 'user_id',
                    'crm.lead': 'user_id',
                    'project.task': 'user_ids',
                }
                
                # Si el modelo está en el mapa, usar ese campo
                if model_name in model_user_fields:
                    user_field = model_user_fields[model_name]
                    _logger.debug(f"   📌 Usando campo mapeado: {user_field}")
                # Si no, intentar detectar el campo automáticamente
                elif 'user_id' in self._fields:
                    user_field = 'user_id'
                    _logger.debug(f"   📌 Usando campo genérico: user_id")
                elif 'user_ids' in self._fields:
                    user_field = 'user_ids'
                    _logger.debug(f"   📌 Usando campo genérico: user_ids")
                elif 'create_uid' in self._fields:
                    # Fallback: filtrar por quien creó el registro
                    user_field = 'create_uid'
                    _logger.debug(f"   📌 Fallback a create_uid (creador del registro)")
                else:
                    # El modelo no tiene ningún campo de usuario conocido
                    # (p. ej. vistas SQL de reportes como account.invoice.report)
                    # No aplicar filtro para evitar errores de campo inválido
                    _logger.debug(
                        f"   ⚠️ {model_name} no tiene campo de usuario conocido, "
                        f"omitiendo filtro 'Solo Mis Documentos'"
                    )
                    user_field = None

                # Agregar el filtro solo si encontramos un campo válido
                if user_field:
                    domain.append((user_field, '=', self.env.user.id))
                    _logger.debug(f"   Dominio modificado: {domain}")
        
        return super(BaseModelExtension, self).web_search_read(domain, specification, offset, limit, order, count_limit)

    def web_read(self, specification, **kwargs):
        """
        Override web_read para bloquear apertura de fichas de productos.

        ESTRATEGIA FINAL — MARKERS DE CAMPOS EXCLUSIVOS DEL FORMULARIO:
        ─────────────────────────────────────────────────────────────────
        Los métodos anteriores fallaban por dos razones:

        1. `len(self) == 1` — Odoo 18 hace prefetch y agrupa varios registros
           en una sola llamada web_read, por lo que len(self) > 1 incluso cuando
           el usuario abre UNA ficha. El guard no se activaba.

        2. Threshold en len(specification) — la spec de la vista de formulario
           puede ser pequeña (Odoo 18 a veces usa lazy-loading por pestañas) y
           la spec relacional puede ser grande (muchos campos en líneas de pedido).

        SOLUCIÓN DEFINITIVA: identificar campos que SOLO aparecen en la spec de
        una carga de vista de formulario de producto y NUNCA en cargas relacionales
        (product_id en líneas de pedido, factura, etc.):

          • attribute_line_ids: configuraciones de variantes — EXCLUSIVO de
            product.template form. Jamás se pide al leer product_id en una línea.
          • product_variant_ids: lista de variantes creadas — EXCLUSIVO form.
          • route_ids: rutas de inventario — solo en la pestaña Inventario del form.
          • packaging_ids: embalajes — solo en la pestaña Embalaje del form.
          • sale_line_warn: configuración aviso al vender — solo en pestaña Ventas.

        Regla de acceso simplificada:
          • Usuario CON config activa en el módulo → NO puede abrir fichas.
          • Usuario SIN config (p.ej. admin inventario sin restricciones) → libre.
          • Admin sistema (base.group_system) → siempre libre (sale antes).
        """
        if self._name in ('product.product', 'product.template'):
            # Campos exclusivos del formulario de producto.
            # Si CUALQUIERA de estos aparece en la spec, es una carga de form.
            _FORM_MARKERS = frozenset({
                'attribute_line_ids',    # product.template: líneas de atributos
                'product_variant_ids',   # product.template: variantes generadas
                'route_ids',             # pestaña inventario: rutas
                'packaging_ids',         # pestaña embalaje
                'sale_line_warn',        # pestaña ventas: aviso en línea
            })
            if _FORM_MARKERS & specification.keys():
                # Es una carga de formulario directa — verificar permisos
                # Admin sistema → siempre libre
                # Admin Inventario (stock.group_stock_manager) → siempre libre
                # Cualquier otro usuario CON config activa → bloqueado
                if (not self.env.user.has_group('base.group_system')
                        and not self.env.user.has_group('stock.group_stock_manager')):
                    has_config = self.env['user.menu.visibility'].search_count([
                        ('user_id', '=', self.env.user.id),
                        ('active', '=', True),
                    ], limit=1)
                    if has_config:
                        raise UserError(
                            _('❌ ACCESO RESTRINGIDO A PRODUCTOS\n\n'
                              'No tienes permiso para abrir las fichas de productos.\n'
                              'Puedes visualizarlos en las listas pero no acceder a los detalles.')
                        )
        return super(BaseModelExtension, self).web_read(specification, **kwargs)

