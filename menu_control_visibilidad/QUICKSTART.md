# 🚀 QUICKSTART - User Menu Visibility

## ⚡ Inicio Rápido en 3 Pasos

### 1️⃣ Instalación
```bash
# Actualizar lista de módulos en Odoo
# Buscar "User Menu Visibility"
# Click en "Instalar"
```

### 2️⃣ Configuración Básica

#### Ocultar un Menú para un Usuario
1. Ir a: **Visibilidad de Usuario > Configuración de Usuarios**
2. Click en "Crear"
3. Seleccionar el **Usuario**
4. Click en **"Configuración Rápida de Menús"** (carga TODOS los menús y submenús)
5. En la pestaña "Menús", buscar el menú o submenú deseado
6. **Configurar permisos:**
   - **Visible**: ❌ Desmarcar para ocultar el menú completamente
   - **Puede Crear**: ❌ Desmarcar para denegar creación de registros
   - **Puede Editar**: ❌ Desmarcar para denegar edición
   - **Puede Eliminar**: ❌ Desmarcar para denegar eliminación
7. Guardar
8. **Click en "🔄 Refrescar Menús"** para aplicar cambios inmediatamente
9. El usuario debe refrescar su navegador (F5)

#### Ocultar un Campo en una Vista
1. Ir a: **Visibilidad de Usuario > Visibilidad de Campos**
2. Click en "Crear"
3. Completar:
   - **Usuario**: Seleccionar usuario
   - **Modelo**: Por ejemplo `product.product` (Productos)
   - **Campo**: Por ejemplo `location_id` (Ubicación)
   - **Visible**: ❌ Desmarcar para ocultar
4. Guardar

### 3️⃣ Verificación
1. Iniciar sesión con el usuario configurado
2. Verificar que los menús/campos configurados estén ocultos

---

## 📋 Casos de Uso Comunes

### Caso 1: Usuario de Almacén
**Objetivo**: Que solo vea Inventario, no Ventas ni Clientes

```
Usuario: operador_almacen
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Menú: Ventas          → ❌ Oculto (visible = No)
Menú: Clientes        → ❌ Oculto
Menú: Inventario      → ✅ Visible
  └─ Productos        → ✅ Visible + Crear ✅ + Editar ✅ + Eliminar ❌
Menú: Fabricación     → ❌ Oculto
```

### Caso 2: Vendedor sin Precios de Costo
**Objetivo**: Ver productos pero sin precio de costo y sin poder eliminar

```
Usuario: vendedor01
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Menú: Ventas / Productos
  Visible: ✅
  Crear:   ✅
  Editar:  ✅
  Eliminar: ❌ ← No puede borrar productos

Campo en product.product:
  standard_price  → ❌ Oculto
```

### Caso 3: Usuario de Consulta (Solo Lectura)
**Objetivo**: Ver clientes pero sin modificarlos

```
Usuario: consultor_ventas
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Menú: Ventas / Clientes
  Visible: ✅
  Crear:   ❌ ← No puede crear
  Editar:  ❌ ← No puede editar
  Eliminar: ❌ ← No puede eliminar
```

### Caso 4: Control Total de Submenús
**Objetivo**: Ver menú principal pero ocultar ciertos submenús

```
Usuario: asistente_ventas
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Menú: Ventas              → ✅ Visible
  ├─ Pedidos              → ✅ Visible (Crear ✅, Editar ✅, Eliminar ❌)
  ├─ Clientes             → ❌ Oculto ← No ve este submenú
  ├─ Productos            → ✅ Visible (Crear ❌, Editar ✅, Eliminar ❌)
  └─ Informes             → ✅ Visible (Solo lectura)
```

---

## 🎯 Accesos Rápidos

| Acción | Ruta |
|--------|------|
| Configurar Usuario | Visibilidad de Usuario > Configuración de Usuarios |
| Gestionar Menús | Visibilidad de Usuario > Visibilidad de Menús |
| Gestionar Campos | Visibilidad de Usuario > Visibilidad de Campos |
| Desde Usuarios | Configuración > Usuarios > Visibilidad Personalizada |

---

## ⚙️ Botones Útiles

**En Configuración de Usuario:**
- 🔵 **Configuración Rápida de Menús**: Carga automáticamente todos los menús principales y submenús
- 🟡 **🔄 Refrescar Menús**: Fuerza la actualización de menús (usar si los cambios no se ven)
- ⚪ **Gestionar Menús**: Abre vista detallada de menús del usuario
- ⚪ **Gestionar Campos**: Abre vista detallada de campos del usuario

--- para cargar todos los menús y submenús
- Agrupa por "Menú Padre" para ver la jerarquía de menús
- Usa los filtros "Menús Principales" y "Submenús" para mejor organización
- Documenta cambios en el campo "Notas"
- Los administradores SIEMPRE ven todo y pueden hacer todo (no se les puede restringir)
- Prueba con el usuario real antes de desplegar

### ⚠️ Importantes
- Las configuraciones son por **usuario**, no por grupo
- Los cambios aplican inmediatamente (puede requerir refrescar navegador)
- Si ocultas un menú padre, los submenús también se ocultan
- Los permisos de crear/editar/eliminar solo funcionan si el menú es visible
- No afecta permisos de seguridad de Odoo, es una capa adicional
- Compatible con grupos estándar de Odoo

### 🎯 Control de Permisos
- **Visible = No**: El usuario NO ve el menú (ni siquiera aparece)
- **Puede Crear = No**: Botón "Crear" deshabilitado o genera error
- **Puede Editar = No**: No puede modificar registros existentes
- **Puede Eliminar = No**: Botón "Eliminar" deshabilitado o genera error
### ⚠️ Importantes
- Las configuraciones son por **usuario**, no por grupo
- Los cambios aplican inmediatamente (puede requerir refrescar navegador)
- No afecta permisos de seguridad, solo visibilidad
- Compatible con grupos estándar de Odoo

### 🔍 Troubleshooting

**Problema: El menú no aparece en la lista**
- Usar "Configuración Rápida" para cargar todos los menús y submenús
- O agregar manualmente desde Visibilidad de Menús

**Problema: Los cambios no aplican / El menú sigue oculto aunque lo activé ⚠️**
1. **Click en el botón "🔄 Refrescar Menús"** en el formulario de configuración (el botón amarillo)
2. El usuario afectado debe **refrescar el navegador (F5 o Ctrl+F5)**
3. Si persiste, cerrar sesión y volver a entrar
4. Verificar que:
   - El campo "Visible" esté marcado (✅)
   - El campo "Activo" esté marcado (✅)
   - No haya registros duplicados para el mismo menú

**Problema: No se oculta el menú**
- Verificar que el usuario no sea administrador (los admin ven todo siempre)

**Problema: Campo sigue visible**
- Refrescar navegador (Ctrl+F5)

**Problema: No aparece el módulo**
- Verificar que esté en custom_addons/
- Reiniciar servicio de Odoo
- Modo desarrollador: Actualizar lista de aplicaciones

### 💡 Importante sobre Cache
- **Los menús se cachean**: Después de hacer cambios, SIEMPRE usa el botón "🔄 Refrescar Menús"
- **El navegador también cachea**: Refresca con F5 o Ctrl+F5 después de cambios
- **Los cambios no son instantáneos**: Pueden tardar unos segundos en aplicarse

---
(C:✅ E:✅ D:❌)      │
│  │  ├─ ❌ Clientes      ← OCULTO        │
│  │  └─ ✅ Productos (C:❌ E:✅ D:❌)    │
│  ├─ ✅ Inventario                       │
│  │  ├─ ✅ Productos (C:✅ E:✅ D:✅)    │
│  │  └─ ✅ Ubicaciones (C:❌ E:❌ D:❌)  │
│  └─ ❌ Contabilidad     ← OCULTO        │
│                                         │
│  📍 Campos                              │
│  ├─ Modelo: product.product             │
│  │  ├─ ✅ Nombre                        │
│  │  ├─ ❌ Ubicación     ← OCULTO        │
│  │  └─ ❌ Costo         ← OCULTO        │
│                                         │
└─────────────────────────────────────────┘

Leyenda: C=Crear, E=Editar, D=Eliminar
│  ├─ ✅ Inventario                       │
│  └─ ❌ Contabilidad     ← OCULTO        │
│                                         │
│  📍 Campos                              │
│  ├─ Modelo: product.product             │
│  │  ├─ ✅ Nombre                        │
│  │  ├─ ❌ Ubicación     ← OCULTO        │
│  │  └─ ❌ Costo         ← OCULTO        │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🆘 ¿Necesitas Ayuda?

1. Revisa el [README.md](README.md) completo
2. Consulta los logs de Odoo para errores
3. Contacta al equipo de desarrollo

---

**¡Listo para usar! 🎉**

El módulo está configurado y funcionando. Los usuarios verán solo lo que configuraste para ellos.
