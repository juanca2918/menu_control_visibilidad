# 📦 Instalación y Configuración del Módulo

## 🔧 Pasos de Instalación

### 1. Copiar el Módulo
El módulo ya está ubicado en:
```
d:\entorno_desarrollo\siteco_odoo_devel\custom_addons\menu_control_visibilidad\
```

### 2. Actualizar Odoo
```bash
# Opción 1: Desde línea de comandos
python odoo-bin -u menu_control_visibilidad -d nombre_base_datos

# Opción 2: Desde la interfaz web
# 1. Ir a Aplicaciones
# 2. Click en "Actualizar lista de aplicaciones"
# 3. Buscar "User Menu Visibility"
# 4. Click en "Instalar"
```

### 3. Verificar Instalación
1. Iniciar sesión como administrador
2. Buscar el menú **"Visibilidad de Usuario"** en el menú principal
3. También disponible en **Configuración > Usuarios > Visibilidad Personalizada**

---

## 🎯 Configuración Inicial

### Primer Uso: Configurar un Usuario

1. **Acceder al módulo**
   - Ir a: `Visibilidad de Usuario > Configuración de Usuarios`

2. **Crear configuración**
   - Click en "Crear"
   - Seleccionar el usuario a configurar

3. **Configurar menús rápidos**
   - Click en botón `"Configuración Rápida de Menús"`
   - Esto carga automáticamente todos los menús principales

4. **Personalizar visibilidad**
   - En la pestaña "Menús":
     - ✅ Marcar = El usuario VE el menú
     - ❌ Desmarcar = El usuario NO ve el menú
   
5. **Guardar**
   - Click en "Guardar"
   - Los cambios aplican inmediatamente

---

## 📋 Ejemplos Prácticos

### Ejemplo 1: Usuario de Almacén
```
Usuario: operador_bodega
────────────────────────────────────────
Objetivo: Solo debe ver Inventario

Configuración:
├─ Ventas          → ❌ Desmarcar
├─ CRM             → ❌ Desmarcar
├─ Inventario      → ✅ Mantener
├─ Contabilidad    → ❌ Desmarcar
└─ Compras         → ❌ Desmarcar
```

### Ejemplo 2: Vendedor sin Costos
```
Usuario: vendedor01
────────────────────────────────────────
Objetivo: Ver productos sin precio de costo

1. Ir a: Visibilidad de Usuario > Visibilidad de Campos
2. Crear nuevo registro:
   - Usuario: vendedor01
   - Modelo: product.product
   - Campo: standard_price
   - Visible: ❌ Desmarcar
3. Guardar
```

### Ejemplo 3: Usuario sin Clientes
```
Usuario: operador_ventas
────────────────────────────────────────
Objetivo: Acceder a Ventas pero sin ver Clientes

En Configuración de Usuario:
└─ Ventas
   ├─ Pedidos          → ✅ Visible
   ├─ Clientes         → ❌ Ocultar ← IMPORTANTE
   └─ Productos        → ✅ Visible
```

---

## 🛠️ Estructura del Módulo

```
menu_control_visibilidad/
├── __init__.py                 # Inicialización del módulo
├── __manifest__.py             # Manifiesto con dependencias
├── README.md                   # Documentación completa
├── QUICKSTART.md               # Guía rápida
├── CHANGELOG.md                # Historial de versiones
├── INSTALL.md                  # Este archivo
│
├── models/                     # Modelos de datos
│   ├── __init__.py
│   ├── menu_visibility.py      # Modelo para menús
│   ├── field_visibility.py     # Modelo para campos
│   └── user_visibility_config.py  # Configuración general
│
├── views/                      # Vistas XML
│   ├── menu_visibility_views.xml
│   ├── field_visibility_views.xml
│   ├── user_visibility_config_views.xml
│   └── menu_items.xml          # Menús del módulo
│
├── security/                   # Permisos
│   └── ir.model.access.csv     # Reglas de acceso
│
└── static/                     # Recursos estáticos
    ├── description/
    │   └── icon.png            # Icono del módulo
    └── src/
        └── js/
            └── menu_visibility.js  # Lógica JavaScript
```

---

## ✅ Checklist Post-Instalación

- [ ] Módulo instalado correctamente
- [ ] Menú "Visibilidad de Usuario" visible para administrador
- [ ] Crear configuración de prueba para un usuario
- [ ] Configurar al menos un menú oculto
- [ ] Iniciar sesión con el usuario de prueba
- [ ] Verificar que el menú esté oculto
- [ ] Probar configuración de campo oculto
- [ ] Documentar configuraciones en campo "Notas"

---

## ⚠️ Notas Importantes

### Permisos
- Solo usuarios con perfil **Administrador** pueden configurar visibilidades
- Los usuarios normales solo leen su propia configuración
- Los administradores SIEMPRE ven todo (no se les puede ocultar nada)

### Comportamiento
- Los cambios aplican inmediatamente
- Puede requerir refrescar el navegador (F5 o Ctrl+F5)
- No afecta permisos de seguridad, solo visibilidad
- Compatible con grupos de seguridad existentes

### Performance
- El módulo carga las configuraciones al iniciar sesión
- Mínimo impacto en rendimiento
- Cache automático de configuraciones

---

## 🐛 Troubleshooting

### Problema: El menú no está en la lista
**Solución**: 
- Usar "Configuración Rápida" para cargar menús principales
- O agregar manualmente desde Visibilidad de Menús

### Problema: Los cambios no aplican
**Solución**:
1. Verificar que el usuario no sea administrador
2. Refrescar navegador (Ctrl+F5)
3. Cerrar sesión y volver a entrar
4. Verificar que la configuración esté "Activa"

### Problema: No aparece el módulo
**Solución**:
1. Verificar que esté en custom_addons/
2. Reiniciar servicio de Odoo
3. Modo desarrollador: Actualizar lista de aplicaciones
4. Verificar logs de Odoo para errores

---

## 📞 Soporte

Para reportar problemas:
1. Revisar este documento completo
2. Revisar [README.md](README.md)
3. Revisar [QUICKSTART.md](QUICKSTART.md)
4. Revisar logs de Odoo
5. Contactar al equipo de desarrollo

---

## 📊 Dependencias

- `base` - Módulo base de Odoo
- `web` - Framework web de Odoo

**Versión Odoo**: 18.0

---

## 🎓 Recursos Adicionales

- [README.md](README.md) - Documentación completa
- [QUICKSTART.md](QUICKSTART.md) - Guía rápida con ejemplos visuales
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios y roadmap

---

**¡Todo listo! El módulo está instalado y funcionando.** 🎉
