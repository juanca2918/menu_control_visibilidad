# Vista Jerárquica de Menús - Guía Rápida

## 📊 Cómo se verá la nueva vista

### Estilo de Tabla Jerárquica

La vista ahora se parece a sistemas POS tradicionales, mostrando:

```
┌─────────────────────┬────────────────────────────┬─────┬───────┬────────┬────────┐
│ 📁 Menú Principal   │ 📋 Opción / Submenú        │ ✅  │  ➕   │   ✏️   │   🗑️   │
│                     │                            │ Ver │ Crear │ Editar │ Borrar │
├═════════════════════╪════════════════════════════╪═════╪═══════╪════════╪════════┤
│ Ventas              │ Ventas                     │ ☑   │  ☑    │   ☑    │   ☑    │ <- Menú principal (negrita, fondo gris)
│ Ventas              │    Clientes                │ ☑   │  ☑    │   ☑    │   ☐    │ <- Submenú (indentado, fondo azul)
│ Ventas              │    Vendedores              │ ☑   │  ☐    │   ☑    │   ☐    │
│ Ventas              │    Promociones             │ ☑   │  ☑    │   ☑    │   ☑    │
│ Ventas              │    Condiciones y Formas... │ ☑   │  ☐    │   ☐    │   ☐    │
│ Ventas              │    Conceptos de Caja       │ ☑   │  ☑    │   ☑    │   ☐    │
│ Ventas              │    Programación Facturas   │ ☑   │  ☐    │   ☐    │   ☐    │
├─────────────────────┼────────────────────────────┼─────┼───────┼────────┼────────┤
│ Inventario          │ Inventario                 │ ☑   │  ☑    │   ☑    │   ☑    │ <- Siguiente menú principal
│ Inventario          │    Ingreso Inventario      │ ☑   │  ☑    │   ☐    │   ☐    │
│ Inventario          │    Productos               │ ☑   │  ☐    │   ☑    │   ☐    │
└─────────────────────┴────────────────────────────┴─────┴───────┴────────┴────────┘
```

## 🎯 Características Visuales

### 1. **Menús Principales** (en negrita, fondo gris)
- Son las primeras filas de cada grupo
- Aparecen en **negrita**
- Fondo gris claro (#f0f0f0)
- Ejemplo: "Ventas", "Inventario", "Contabilidad"

### 2. **Submenús** (indentados, fondo azul claro)
- Aparecen debajo de su menú principal
- Fondo azul muy claro (#fafbfc)
- Indentación visual de 30px en la columna "Opción"
- Ejemplo: "Clientes", "Productos", "Pedidos"

### 3. **Checkboxes de Permisos**
- **✅ Ver**: Si el usuario puede ver este menú/opción
- **➕ Crear**: Si puede crear nuevos registros
- **✏️ Editar**: Si puede modificar registros existentes
- **🗑️ Borrar**: Si puede eliminar registros

## 📝 Cómo usar la vista

### Paso 1: Abrir Configuración de Usuario
1. Ir a **Configuración → Usuarios → User Menu Visibility → Configurar Usuario**
2. O ir a **Configuración → Técnico → User Menu Visibility**

### Paso 2: Configuración Rápida
1. Seleccionar un usuario
2. Hacer clic en **"Configuración Rápida de Menús"**
3. Se cargarán TODOS los menús del sistema

### Paso 3: Ver la Vista Jerárquica
Ahora verás una tabla donde:
- **Columna 1**: Menú Principal (Ventas, Inventario, etc.)
- **Columna 2**: La opción específica dentro de ese menú
- **Columnas 3-6**: Checkboxes para permisos

### Paso 4: Asignar Permisos
1. Haz clic en cualquier checkbox para cambiar el permiso
2. Los cambios se guardan automáticamente (edición inline)
3. Para ocultar completamente un menú:
   - Desactiva "✅ Ver" en el menú principal
   - Automáticamente se ocultan todos sus submenús

## 💡 Ejemplos de Uso

### Ejemplo 1: Usuario que ve Ventas pero no puede eliminar
```
Ventas → Ventas:          ✅ Ver ✓  ➕ Crear ✓  ✏️ Editar ✓  🗑️ Borrar ✗
Ventas → Clientes:        ✅ Ver ✓  ➕ Crear ✓  ✏️ Editar ✓  🗑️ Borrar ✗
Ventas → Vendedores:      ✅ Ver ✓  ➕ Crear ✗  ✏️ Editar ✗  🗑️ Borrar ✗
```
**Resultado**: Ve todo Ventas, puede crear/editar clientes, pero NO eliminar nada

### Ejemplo 2: Ocultar completamente Clientes
```
Ventas → Ventas:          ✅ Ver ✓  ➕ Crear ✓  ✏️ Editar ✓  🗑️ Borrar ✓
Ventas → Clientes:        ✅ Ver ✗  ➕ Crear ✗  ✏️ Editar ✗  🗑️ Borrar ✗
Ventas → Productos:       ✅ Ver ✓  ➕ Crear ✓  ✏️ Editar ✓  🗑️ Borrar ✗
```
**Resultado**: No verá la opción "Clientes" en el menú Ventas

### Ejemplo 3: Solo lectura en Inventario
```
Inventario → Inventario:     ✅ Ver ✓  ➕ Crear ✗  ✏️ Editar ✗  🗑️ Borrar ✗
Inventario → Productos:      ✅ Ver ✓  ➕ Crear ✗  ✏️ Editar ✗  🗑️ Borrar ✗
```
**Resultado**: Puede ver todo Inventario pero solo consultar, sin modificar

## 🎨 Orden Automático

La vista ordena automáticamente por:
1. **Primero**: Menú Principal (alfabético)
2. **Segundo**: Submenús dentro de cada menú principal (alfabético)

Esto significa que verás agrupados:
- Todos los elementos de "Contabilidad" juntos
- Todos los elementos de "Inventario" juntos
- Todos los elementos de "Ventas" juntos
- etc.

## 🔄 Aplicar Cambios

Después de configurar los permisos:
1. Los cambios se guardan automáticamente
2. El cache se invalida automáticamente
3. **IMPORTANTE**: El usuario debe **refrescar su navegador (F5)** para ver los cambios

## ✨ Ventajas de esta Vista

✅ **Visual**: Fácil de entender de un vistazo
✅ **Jerárquica**: Ves claramente menú padre → opciones
✅ **Rápida**: Edición inline sin abrir formularios
✅ **Ordenada**: Todo agrupado lógicamente
✅ **Completa**: Todos los menús del sistema en un solo lugar
✅ **Familiar**: Similar a sistemas POS que ya conoces

## 🆘 Solución de Problemas

### Los cambios no se ven
- El usuario debe **refrescar (F5)** el navegador
- Si persiste, cerrar sesión y volver a entrar

### No aparecen todos los menús
- Usar el botón **"Configuración Rápida de Menús"**
- Esto cargará todos los menús del sistema

### Los submenús no se ocultan
- Asegúrate de desactivar "✅ Ver" en el submenú específico
- Desactivar el menú padre NO oculta automáticamente los hijos
