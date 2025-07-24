# La Venezolana de Seguros y Vida - Módulo Odoo 16

## Descripción

Módulo completo para la gestión de pólizas de seguros vehiculares de "La Venezolana de Seguros y Vida" desarrollado para Odoo 16.

## Características Principales

### ✅ Gestión Completa de Pólizas
- **Numeración automática** de pólizas con secuencia personalizable
- **Estados de póliza**: Borrador, Activa, Vencida, Cancelada
- **Seguimiento completo** de vigencias y vencimientos
- **Integración con el sistema de mensajería** de Odoo

### ✅ Datos del Tomador y Asegurado
- Registro completo de tomadores y asegurados
- Validación de cédulas/RIF únicos
- Información de contacto detallada
- Historial de pólizas por persona

### ✅ Gestión de Vehículos
- Registro detallado de vehículos
- Validación de placas y seriales únicos
- Control de pólizas activas por vehículo
- Información técnica completa

### ✅ Reportes Profesionales
- **Póliza completa** con todos los datos requeridos
- **Carnet RCV** (Responsabilidad Civil Vehicular) listo para imprimir
- Formato profesional adaptado a los estándares venezolanos

### ✅ Funcionalidades Avanzadas
- Búsquedas inteligentes por múltiples criterios
- Filtros predefinidos para estados y fechas
- Agrupaciones por diferentes campos
- Validaciones automáticas de datos

## Instalación

### Requisitos Previos
- Odoo 16.0 o superior
- Acceso de administrador al sistema

### Pasos de Instalación

1. **Copiar el módulo**
   ```bash
   cp -r LaVenezolana16 /path/to/odoo/addons/
   ```

2. **Actualizar lista de aplicaciones**
   - Ir a Aplicaciones
   - Hacer clic en "Actualizar lista de aplicaciones"

3. **Instalar el módulo**
   - Buscar "La Venezolana de Seguros y Vida"
   - Hacer clic en "Instalar"

## Configuración Inicial

### 1. Configurar Secuencia de Pólizas
- Ir a **Configuración > Secuencias**
- Buscar "Secuencia Póliza de Seguro"
- Ajustar prefijo y numeración según necesidades

### 2. Crear Datos Maestros
1. **Tomadores/Asegurados**
   - Ir a **La Venezolana Seguros > Configuración > Tomadores/Asegurados**
   - Registrar clientes frecuentes

2. **Vehículos**
   - Ir a **La Venezolana Seguros > Configuración > Vehículos**
   - Registrar vehículos a asegurar

## Uso del Sistema

### Crear una Nueva Póliza

1. **Acceder al módulo**
   - Ir a **La Venezolana Seguros > Pólizas > Pólizas de Seguro**

2. **Crear nueva póliza**
   - Hacer clic en "Crear"
   - El número de póliza se genera automáticamente

3. **Completar información**
   - **Tomador y Asegurado**: Seleccionar o crear nuevos
   - **Datos de la Póliza**: Vigencias, tipo de pago, sucursal, etc.
   - **Datos del Recibo**: Información de facturación
   - **Vehículo**: Seleccionar o registrar nuevo vehículo
   - **Cobertura**: Límites y gastos cubiertos

4. **Activar póliza**
   - Hacer clic en "Activar" para poner la póliza en vigencia

### Generar Reportes

#### Póliza Completa
1. Abrir la póliza deseada
2. Hacer clic en "Imprimir" > "Póliza de Seguro"
3. Se genera un PDF con todos los datos

#### Carnet RCV
1. Abrir la póliza deseada
2. Hacer clic en "Imprimir" > "Carnet RCV"
3. Se genera un carnet listo para cortar e imprimir

## Estructura de Datos

### Campos Principales de la Póliza

#### Datos del Tomador
- Tomador (relación con tomadores)
- Cédula/RIF del tomador
- Asegurado (relación con tomadores)
- Cédula/RIF del asegurado
- Dirección y teléfono

#### Datos de la Póliza
- Vigencia (desde/hasta/hora)
- Tipo de pago
- Sucursal
- Canal de venta
- Frecuencia de pago
- Código de intermediarios
- Participación
- Moneda

#### Datos del Recibo
- Vigencia del recibo
- Tipo de movimiento
- Total a pagar

#### Datos del Vehículo
- Marca, modelo, año
- Placa, serial motor, serial carrocería
- Color, tipo, uso
- Número de puestos

#### Cobertura
- Exceso límite
- Muerte e invalidez
- Daños a cosas
- Defensa penal
- Gastos médicos
- Gastos funerarios

## Validaciones Implementadas

- ✅ **Cédulas/RIF únicos** por tomador/asegurado
- ✅ **Placas únicas** por vehículo
- ✅ **Seriales únicos** (motor y carrocería)
- ✅ **Años válidos** para vehículos
- ✅ **Vigencias automáticas** (1 año desde fecha inicio)

## Funcionalidades Adicionales

### Búsquedas Inteligentes
- Buscar pólizas por número, tomador, asegurado o placa
- Buscar tomadores por nombre o cédula
- Buscar vehículos por marca, modelo o placa

### Filtros Predefinidos
- Pólizas activas, vencidas, canceladas
- Vehículos con/sin póliza activa
- Tomadores con pólizas

### Estados Automáticos
- Control automático de vencimientos
- Cambio de estado a "vencida" cuando expira la vigencia

## Soporte y Mantenimiento

### Tareas de Mantenimiento Recomendadas

1. **Verificación de vencimientos**
   - Ejecutar manualmente: `env['poliza.seguro'].check_expired_policies()`
   - O configurar un cron job automático

2. **Respaldos regulares**
   - Respaldar datos de pólizas mensualmente
   - Mantener histórico de reportes generados

### Personalización

El módulo está diseñado para ser fácilmente personalizable:

- **Campos adicionales**: Agregar en los modelos correspondientes
- **Reportes personalizados**: Modificar templates XML
- **Validaciones específicas**: Extender métodos de validación
- **Flujos de trabajo**: Personalizar estados y transiciones

## Contacto y Soporte

Para soporte técnico o personalizaciones adicionales, contactar al equipo de desarrollo.

---

**Versión**: 16.0.1.0.0  
**Compatibilidad**: Odoo 16.0+  
**Licencia**: LGPL-3  
**Desarrollado para**: La Venezolana de Seguros y Vida