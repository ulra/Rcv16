# Generador de Diseños desde PDF

## Descripción
Esta funcionalidad permite a los administradores del sistema subir un archivo PDF con un diseño de referencia (póliza o carnet RCV) para que el módulo analice automáticamente su estructura y genere templates personalizados.

## Características Principales

### 🎨 Análisis Automático de PDF
- Extrae elementos de diseño (texto, imágenes, colores, tipografías)
- Analiza la estructura y layout del documento
- Detecta posiciones y dimensiones de elementos

### 🔧 Generación de Templates
- Convierte automáticamente el diseño a formato XML de Odoo
- Mantiene la estructura visual del PDF original
- Genera código compatible con el sistema de reportes

### 👀 Vista Previa
- Muestra una vista previa del diseño generado
- Permite revisar antes de aplicar los cambios
- Incluye información detallada del análisis

### 🔒 Seguridad y Backup
- Solo accesible para administradores del sistema
- Hace backup automático del diseño original
- Permite restaurar el diseño anterior si es necesario

## Cómo Usar

### Método 1: Asistente Rápido
1. Ve a **Configuración > Generar desde PDF**
2. Sube tu archivo PDF de referencia
3. Selecciona el tipo de diseño (Carnet RCV, Póliza, o Ambos)
4. Haz clic en "Generar Diseño"
5. Revisa la vista previa y aplica si está correcto

### Método 2: Gestión Completa
1. Ve a **Configuración > Generador de Diseños**
2. Crea un nuevo registro
3. Sube el PDF y configura las opciones
4. Usa "Analizar PDF" para procesar el archivo
5. Revisa los resultados en las pestañas de análisis
6. Aplica el diseño cuando esté listo

## Tipos de Diseño Soportados

### 📄 Carnet RCV
- Formato compacto (85mm x 54mm)
- Incluye todos los campos requeridos
- Optimizado para impresión en tarjetas

### 📋 Póliza Completa
- Formato de página completa
- Layout personalizable
- Incluye encabezados y pie de página

### 🔄 Ambos
- Genera templates para carnet y póliza
- Mantiene consistencia visual entre ambos

## Requisitos Técnicos

### Dependencias de Python
```bash
pip install PyPDF2>=3.0.0
pip install PyMuPDF>=1.23.0
pip install Pillow>=9.0.0
```

### Formatos de PDF Recomendados
- PDFs creados digitalmente (no escaneados)
- Texto seleccionable y legible
- Resolución mínima de 300 DPI
- Tamaño máximo de 10 MB

## Estados del Generador

| Estado | Descripción |
|--------|-------------|
| **Borrador** | Recién creado, listo para subir PDF |
| **Analizando** | Procesando el archivo PDF |
| **Listo** | Análisis completado, listo para aplicar |
| **Aplicado** | Diseño aplicado a los reportes |
| **Error** | Error en el procesamiento |

## Funciones Avanzadas

### 🔍 Análisis Detallado
- Extracción de metadatos del PDF
- Detección de fuentes y colores
- Mapeo de posiciones de elementos
- Identificación de imágenes y gráficos

### 🛠️ Personalización
- Edición manual del template generado
- Ajustes de posicionamiento
- Modificación de estilos CSS
- Integración con campos dinámicos

### 📊 Gestión de Versiones
- Historial de diseños aplicados
- Comparación entre versiones
- Rollback a versiones anteriores
- Backup automático

## Solución de Problemas

### Error: "PyPDF2 not installed"
```bash
pip install PyPDF2 PyMuPDF
```

### Error: "PDF no válido"
- Verifica que el archivo sea un PDF real
- Intenta con un PDF diferente
- Asegúrate de que no esté corrupto

### Error: "No se pueden extraer elementos"
- Usa un PDF con texto seleccionable
- Evita PDFs escaneados o de baja calidad
- Verifica que el PDF no esté protegido

### Diseño no se aplica correctamente
- Revisa la vista previa antes de aplicar
- Verifica que los campos dinámicos estén correctos
- Usa la función de restaurar backup si es necesario

## Mejores Prácticas

### 📋 Preparación del PDF
1. Usa PDFs de alta calidad
2. Asegúrate de que el texto sea seleccionable
3. Incluye todos los elementos necesarios
4. Mantén un diseño limpio y organizado

### 🎯 Configuración
1. Haz siempre backup antes de aplicar
2. Prueba con un diseño simple primero
3. Revisa la vista previa cuidadosamente
4. Documenta los cambios realizados

### 🔧 Mantenimiento
1. Mantén un registro de diseños aplicados
2. Actualiza las dependencias regularmente
3. Prueba los reportes después de aplicar cambios
4. Mantén backups de diseños importantes

## Limitaciones Actuales

- Solo procesa la primera página del PDF
- Limitado a elementos básicos (texto, imágenes)
- No soporta elementos interactivos
- Requiere ajustes manuales para diseños complejos

## Roadmap Futuro

- [ ] Soporte para múltiples páginas
- [ ] Detección automática de campos
- [ ] Editor visual de templates
- [ ] Importación desde otros formatos (Word, etc.)
- [ ] Plantillas predefinidas
- [ ] Integración con herramientas de diseño

---

**Nota**: Esta funcionalidad está diseñada para administradores del sistema. Requiere conocimientos básicos de XML y CSS para ajustes avanzados.