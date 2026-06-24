# Visibilidad de Menús por Usuario

**Odoo 18.0** | Administración | `OPL-1` | Por Consultores Odoo Colombia

Controla exactamente qué puede **ver** y **hacer** cada usuario en Odoo, sin tocar grupos de seguridad ni escribir una sola línea de código.

---

## Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| 👁️ **Visibilidad de menús** | Muestra/oculta cualquier menú por usuario. Ocultar un padre oculta todos sus hijos automáticamente. |
| 🔐 **Permisos CRUD por menú** | Crear / Editar / Eliminar independientes por menú, incluso para menús que comparten modelo (Cotizaciones ≠ Pedidos de Venta). |
| 📄 **Filtro "Solo Mis Documentos"** | Interruptor por menú o global: restringe las listas a los registros creados por o asignados al usuario actual. |
| 🚫 **Bloqueo de fichas de producto** | Impide abrir fichas individuales de productos sin desactivar el modelo. |
| ⚡ **Efecto instantáneo** | Los cambios se aplican de inmediato, sin reiniciar el servidor. |
| 🗂️ **Carga masiva de menús** | Botón (solo admin) para importar todos los menús del sistema en un clic. |
| 🧩 **Visibilidad de campos** | Oculta campos específicos por modelo y usuario (opcional). |

## Cómo funciona

Sobreescribe `get_views()` en el modelo `base` de Odoo para modificar el arch de la vista **en memoria** antes de enviarla al navegador. Ajusta dinámicamente los atributos `create`, `edit`, `delete`, `duplicate` e `import` por usuario/menú. Sin modificaciones en la base de datos — invisible para los demás usuarios.

La detección de menús usa `options.action_id` (Odoo 18 siempre lo envía), por lo que los menús que comparten el mismo modelo (p. ej. `sale.order`) siempre se tratan de forma independiente.

## Idiomas

El módulo incluye traducciones para **inglés (en_US)** y **español – Colombia (es_CO)**. Los textos de la interfaz están en español por defecto; instala la traducción al inglés (`en_US`) si deseas usarlo en inglés.

## Instalación

```bash
# 1. Copia el módulo a tu addons path (p. ej. custom_addons)
# 2. Actualiza la lista de aplicaciones e instala, o:
python odoo-bin -c odoo.conf -d TU_BD -u menu_control_visibilidad
```

O instala directamente desde **Aplicaciones** en el backend de Odoo. Depende de `base`, `web`, `bus`.

## Inicio rápido

1. Ve a **Visibilidad de Usuario → Configuración de Usuarios**
2. Haz clic en **Nuevo** y selecciona un usuario
3. Haz clic en **⚡ Cargar Todos los Menús** (solo admin)
4. Activa/desactiva visibilidad y permisos en cada fila de menú
5. Guarda — el efecto es inmediato

## Casos de uso comunes

- **Vendedor** que puede ver Cotizaciones pero no crearlas ni eliminarlas.
- **Contador** que ve Facturas pero no tiene acceso a Notas de Crédito.
- **Operario de almacén** que trabaja con Albaranes pero nunca ve Clientes.
- **Gerente** que revisa todos los pedidos pero no puede eliminar ningún registro.
- Cualquier perfil de acceso personalizado — sin Python ni nuevos grupos de seguridad.

## Permisos

- **Administradores** (`base.group_system`): acceso completo a la configuración; siempre ven todos los menús y campos.
- **Usuarios internos**: se les aplica la configuración guardada en su sesión.

## Registro de cambios

Consulta [CHANGELOG.md](CHANGELOG.md) para el historial completo de versiones.

## Soporte

- **Autor:** Consultores Odoo Colombia
- **Sitio web:** https://consultoresodoocolombia.odoo.com
- **Correo:** siteco@outlook.com

## Licencia

`OPL-1` — Odoo Proprietary License v1.0. Consulta el archivo [LICENSE](LICENSE) para más detalles.
