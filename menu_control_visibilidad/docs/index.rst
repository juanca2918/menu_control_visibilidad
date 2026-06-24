Visibilidad y Permisos de Menús por Usuario
===========================================

.. toctree::
   :maxdepth: 2
   :caption: Contenido:

Resumen
-------
Controla exactamente qué puede ver y hacer cada usuario en Odoo: visibilidad de menús y permisos CRUD por usuario, sin modificar grupos de seguridad ni escribir código.

Descripción
-----------
Este módulo entrega a los administradores un panel central para controlar, por usuario, qué menús son visibles y qué operaciones (Crear, Editar, Eliminar) están permitidas. Los permisos se aplican en tiempo de ejecución modificando el arch de la vista en memoria, por lo que no se tocan grupos de seguridad, reglas de registro ni registros de vista en la base de datos.

Funcionalidades
---------------
* **Visibilidad de menús por usuario:** oculta o muestra cualquier menú con un simple interruptor. Ocultar un menú padre oculta automáticamente sus hijos.
* **Permisos CRUD independientes:** controla Crear / Editar / Eliminar por menú, incluso para menús que comparten el mismo modelo — Cotizaciones y Pedidos de Venta, o Facturas y Notas de Crédito, siempre se gestionan por separado (detección por acción).
* **Filtro "Solo Mis Documentos":** interruptor por menú o global que restringe las listas a los registros creados por o asignados al usuario actual.
* **Bloqueo de fichas de producto:** impide que los usuarios abran fichas individuales de productos desde cualquier menú, sin desactivar el modelo completo.
* **Efecto instantáneo:** los cambios de permisos se aplican de inmediato para el usuario — sin reiniciar el servidor ni limpiar caché manualmente.
* **Carga masiva (solo administradores):** botón de un clic para importar todos los menús del sistema en la configuración de un usuario.
* **Visibilidad de campos (opcional):** oculta campos específicos por modelo y usuario.

Cómo funciona
-------------
El módulo sobreescribe ``get_views()`` en el modelo ``base`` para modificar el arch XML en tiempo de ejecución, ajustando los atributos ``create``, ``edit``, ``delete``, ``duplicate`` e ``import`` antes de enviar la vista al navegador. La identificación del menú se basa en ``options.action_id`` (siempre presente en Odoo 18 al cargar una vista desde un menú), garantizando que los menús que comparten el mismo modelo se traten de forma independiente.

Instalación
-----------
Requiere ``base``, ``web`` y ``bus``. Instala desde **Aplicaciones** y abre **Visibilidad de Usuario → Configuración de Usuarios**.

Créditos
--------
* **Autor:** Consultores Odoo Colombia
* **Sitio web:** https://consultoresodoocolombia.odoo.com
* **Soporte:** siteco@outlook.com
