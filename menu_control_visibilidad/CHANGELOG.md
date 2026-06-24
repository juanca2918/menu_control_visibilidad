# Visibilidad de Menús por Usuario - Registro de cambios

Todos los cambios notables de este proyecto se documentan en este archivo.

## [5.7.0] - 2026-06-24

### Documentación e internacionalización
- Se agregaron traducciones oficiales: **inglés (en_US)** y **español – Colombia (es_CO)**, con una plantilla `menu_control_visibilidad.pot` actualizada.
- Se eliminaron archivos de traducción contaminados que pertenecían a otro módulo.
- Se reescribieron `docs/index.rst` y `README.md` para este módulo (antes referenciaban el módulo equivocado).
- Se unificó autor/marca a **Consultores Odoo Colombia** y la licencia a **OPL-1** en manifest, README y la descripción de la App Store.
- Se corrigieron los textos de las capturas en `static/description/index.html` para que coincidan con las imágenes reales.

## [5.6.0] - 2026-03-07

### Mejoras mayores — Control de acceso inteligente

#### Visibilidad de botones — Reglas de flujo refinadas
- Botones **Confirmar / Validar / Aprobar**: visibles para el usuario normal **solo** cuando `can_create=True` (necesario para avanzar el flujo).
- **Todos los demás botones de acción** (Cancelar, Restablecer a Borrador, Nota de Crédito, Revertir, Registrar Pago): siempre ocultos para el usuario normal con configuración activa.
- Botones de **impresión**: siempre visibles sin importar el perfil.
- Los gestores nativos de un módulo de Odoo (detectados por un ID de grupo XML que contiene `manager`/`admin`) siempre ven todos los botones.

#### Pedido de venta confirmado — Solo lectura para el usuario normal
- Una vez confirmada una cotización (`state = 'sale'` o `done`), el usuario normal no puede agregar ni modificar líneas del pedido.
- Implementado mediante una expresión `readonly` inyectada directamente en `order_line` y en los campos de cabecera en `get_views()`, combinándose correctamente con la expresión `locked` nativa de Odoo.

#### Bloqueo de fichas de producto
- Los usuarios con cualquier configuración activa en este módulo **no pueden abrir fichas de producto** desde ningún menú.
- Excepción: los usuarios con `stock.group_stock_manager` (Admin de Inventario) siempre pueden abrirlas.
- `base.group_system` (admin de Odoo) nunca tiene restricciones.
- La detección usa marcadores de campo en la especificación de `web_read()` (`attribute_line_ids`, `product_variant_ids`, `route_ids`, `packaging_ids`, `sale_line_warn`), exclusivos de la carga de fichas de producto.
- Las **listas** de productos siguen siendo siempre accesibles; solo se bloquean las fichas individuales.

#### Reporte de análisis de ventas — Siempre filtrado
- `sale.report`, `account.invoice.report`, `purchase.report` siempre se filtran por el usuario actual (sin necesidad del checkbox "Solo Mis Documentos").
- Implementado como un prefiltro forzado en `web_search_read()`.

#### Eliminado: campo can_pay
- Se eliminó el campo `can_pay` y toda su UI relacionada del modelo, vistas y filtros de búsqueda.
- La migración `18.0.5.6.0` elimina la columna de la BD si existe.

#### Refuerzo de creación de productos
- El grupo nativo de Odoo "Creación de Productos" (`product.group_product_manager`) ahora se refuerza en todos los formularios (facturas, pedidos de compra, cotizaciones) mediante las opciones `no_create`/`no_quick_create` inyectadas en `get_views()`.

#### Correcciones
- `account.invoice.report` (vista SQL): ya no falla con `Invalid field create_uid` cuando el filtro "Solo Mis Documentos" está activo.
- La búsqueda "Ver más" de productos en documentos ahora devuelve el catálogo completo (no filtrado por `create_uid`).
- Los usuarios administradores de cualquier módulo conservan correctamente sus botones de acción.

## [5.5.0] - 2026-03-07

### Lógica de botones por tipo de usuario nativo de Odoo

- **Administrador del sistema** (`base.group_system`): ve todos los botones de todos los formularios sin restricción alguna.
- **Usuario interno normal** (sin `base.group_system`) con configuración activa en el módulo:
  - Se ocultan **TODOS** los botones de acción del `<header>` de los formularios: Confirmar, Pagar, Restablecer a Borrador, Desbloquear, Nota de Crédito, Cancelar, Validar, etc.
  - Los botones de **impresión** (`print`/`report`) permanecen siempre visibles.
  - Los controles CRUD (`can_create`, `can_write`, `can_unlink`) siguen aplicándose mediante atributos del nodo raíz de la vista.

#### Cambios técnicos
- Comentario explicativo añadido al inicio de `get_views()` describiendo los dos perfiles y su comportamiento.
- Todos los `_logger.info` en la ruta caliente cambiados a `_logger.debug` (el aviso de "menú no detectado" también bajado a debug para no saturar los logs en producción).
- Eliminado `live_test_url: ''` del manifest (causaba una advertencia en la App Store).

## [1.4.0] - 2026-03-04

### Vista jerárquica mejorada
- Vista tipo tabla jerárquica inspirada en los sistemas POS tradicionales.
- Orden automático: Menú Principal → Submenús (igual que el menú real de Odoo).
- Columnas claras: "Menú Principal" y "Opción / Submenú".
- Checkboxes visuales: Ver, Crear, Editar, Eliminar.
- Decoraciones visuales: menús principales en negrita con fondo gris claro, submenús con fondo azul claro e indentación, registros inactivos atenuados.
- Nuevo `menu_hierarchy.css` para los estilos jerárquicos e indentación automática de submenús.

## [1.3.0] - 2026-03-04

### Vistas visuales mejoradas
- Vista Kanban con tarjetas visuales y badges de colores por estado (Visible/Oculto/Permisos).
- Avatar de usuario en cada tarjeta; agrupación por defecto por menú padre.
- Emojis en todos los filtros para identificación rápida; filtros de permisos (Crear/Editar/Eliminar) y agrupaciones múltiples (Padre/Usuario/Modelo/Visible/Estado).

## [1.2.1] - 2026-03-04

### Corrección de caché Python
- Botón "Refrescar Menús" removido temporalmente.
- Permite actualizar el módulo sin reiniciar el servidor.
- La caché se invalida automáticamente al guardar.

## [1.2.0] - 2026-03-04

### Sistema de caché mejorado
- Invalidación automática de caché al crear/editar/eliminar configuraciones.
- Método `action_refresh_menus` para forzar un refresco manual.
- Notificación por bus a los usuarios afectados; los cambios se aplican de inmediato.

### Permisos CRUD
- Control de Crear/Editar/Eliminar por menú mediante los campos `can_create`, `can_write`, `can_unlink`.
- Validación en las operaciones de base de datos.

## [1.1.0] - 2026-03-04

### Soporte de submenús
- Campo `parent_menu_id` para la jerarquía de menús.
- Campo calculado `model_name` desde la acción del menú.
- Filtros para menús principales vs submenús y configuración granular por opción.

## [1.0.0] - 2026-03-04

### Características iniciales
- Control de visibilidad de menús por usuario mediante checkboxes y configuración rápida de menús principales.
- Interfaz Kanban para gestión visual con búsqueda y filtros avanzados.
- Control de visibilidad de campos por modelo/usuario con selección dinámica de campos.
- Vista de configuración centralizada por usuario organizada en pestañas.
- Seguridad: permisos para administradores y usuarios; los administradores siempre ven todo.
- Frontend moderno (framework Owl) con interceptación de menús en tiempo real y sin recargar la página.

#### Modelos
- `user.menu.visibility` — configuración de menús
- `user.field.visibility` — configuración de campos
- `user.visibility.config` — configuración general por usuario

## Hoja de ruta

- Plantillas de configuración rápida por rol.
- Importación/exportación y clonación de configuraciones entre usuarios.
- Configuración por grupos (además de por usuario).
- Historial de cambios y auditoría de accesos.
- Restricciones temporales (por horario/fecha).
