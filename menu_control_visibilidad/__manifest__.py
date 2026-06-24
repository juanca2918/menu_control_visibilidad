# -*- coding: utf-8 -*-
{
    'name': 'User Visibility Menu',
    'version': '18.0.5.7.0',
    'category': 'Administration',
    'summary': 'Visibilidad de menús y permisos CRUD por usuario sin modificar grupos de seguridad',
    'description': """
Visibilidad y Permisos de Menús por Usuario
===========================================

Controla exactamente qué puede **ver** y **hacer** cada usuario en Odoo, sin
tocar los grupos de seguridad ni las reglas de registro.

Funcionalidades clave
---------------------
* **Visibilidad de menús por usuario** — muestra u oculta cualquier menú con un
  simple interruptor. Funciona con toda la jerarquía: ocultar un menú padre
  oculta automáticamente sus hijos.
* **Permisos CRUD por menú** — controla de forma independiente los botones
  Crear / Editar / Eliminar de cada menú (por ejemplo, permitir ver Pedidos de
  Venta pero no crearlos).
* **Detección por acción** — Cotizaciones y Pedidos de Venta comparten el mismo
  modelo (sale.order) pero tienen *acciones distintas*, por lo que sus permisos
  son siempre independientes. Igual para Facturas vs Notas de Crédito (account.move).
* **Filtro "Solo Mis Documentos"** — interruptor por menú o global que restringe
  automáticamente las listas a los registros creados o asignados al usuario actual.
* **Bloqueo de fichas de producto** — impide que los usuarios abran las fichas
  individuales de productos desde cualquier menú, sin desactivar el modelo completo.
* **Invalidación de caché instantánea** — los cambios de permisos surten efecto
  de inmediato, sin reiniciar el servidor.
* **Carga masiva (solo Administradores)** — botón de un clic para importar todos
  los menús del sistema en la configuración de un usuario.
* **Visibilidad de campos (opcional)** — oculta campos específicos por modelo y usuario.

Idiomas
-------
Incluye traducciones para **inglés (en_US)** y **español – Colombia (es_CO)**.

Casos de uso
------------
* Vendedor que puede ver pero no crear Cotizaciones.
* Contador que ve Facturas pero no Notas de Crédito.
* Operario de almacén que trabaja con Albaranes pero nunca ve Clientes.
* Gerente que revisa todos los pedidos pero no puede eliminar ninguno.
* Cualquier perfil de acceso personalizado sin escribir código Python ni crear grupos.

Cómo funciona
-------------
El módulo sobreescribe ``get_views()`` en el modelo ``base`` para modificar el
arch XML en tiempo de ejecución, ajustando los atributos ``create``, ``edit``,
``delete``, ``duplicate`` e ``import`` antes de enviar la vista al navegador.
No se modifica ningún registro de vista en la base de datos; cada cambio se
aplica en memoria por petición.
    """,
    'author': 'Consultores Odoo Colombia',
    'website': 'https://consultoresodoocolombia.odoo.com',
    'support': 'siteco@outlook.com',
    'license': 'OPL-1',
    'price': 30.0,
    'currency': 'USD',
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base', 'web', 'bus'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_visibility_views.xml',
        'views/field_visibility_views.xml',
        'views/user_visibility_config_views.xml',
        'views/menu_items.xml',
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'menu_control_visibilidad/static/src/css/menu_hierarchy.css',
            'menu_control_visibilidad/static/src/js/menu_visibility_reload.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
