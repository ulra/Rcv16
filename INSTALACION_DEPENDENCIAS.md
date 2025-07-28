# Instalación de Dependencias PDF - LaVenezolana16

## Problema: "python: command not found"

Este error es común en contenedores de Odoo donde el comando `python` no está disponible, pero `python3` sí lo está.

## Soluciones

### Opción 1: Script Bash (Recomendado para contenedores)

```bash
# Hacer el script ejecutable
chmod +x install_odoo_dependencies.sh

# Ejecutar el script
./install_odoo_dependencies.sh
```

### Opción 2: Script Python mejorado

```bash
# Usar python3 en lugar de python
python3 install_dependencies.py
```

### Opción 3: Instalación manual

#### En el contenedor de Odoo:

```bash
# 1. Acceder al contenedor como root
docker exec -u root -it <nombre_contenedor> bash

# 2. Actualizar paquetes
apt-get update

# 3. Instalar pip si no está disponible
apt-get install -y python3-pip

# 4. Instalar dependencias PDF
pip3 install pypdf PyPDF2 reportlab

# 5. Verificar instalación
python3 -c "import pypdf, PyPDF2, reportlab; print('✓ Todas las librerías instaladas')"

# 6. Reiniciar el contenedor
exit
docker restart <nombre_contenedor>
```

#### Desde el host (Docker Compose):

```bash
# Si usas docker-compose
docker-compose exec -u root odoo bash

# Luego seguir los pasos 2-6 de arriba
```

### Opción 4: Modificar Dockerfile (Solución permanente)

Si tienes acceso al Dockerfile de tu contenedor de Odoo:

```dockerfile
# Añadir estas líneas al Dockerfile
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install pypdf PyPDF2 reportlab
```

Luego reconstruir la imagen:

```bash
docker-compose build
docker-compose up -d
```

## Verificación de la instalación

Después de instalar las dependencias, verifica que todo funcione:

```bash
# Verificar Python
python3 --version

# Verificar pip
pip3 --version

# Verificar librerías PDF
python3 -c "import pypdf; print('pypdf:', pypdf.__version__)"
python3 -c "import PyPDF2; print('PyPDF2:', PyPDF2.__version__)"
python3 -c "import reportlab; print('reportlab:', reportlab.Version)"
```

## Actualización del módulo

Una vez instaladas las dependencias:

1. **Reiniciar Odoo:**
   ```bash
   docker restart <nombre_contenedor>
   # o
   docker-compose restart odoo
   ```

2. **Actualizar el módulo en Odoo:**
   - Ir a Aplicaciones
   - Buscar "LaVenezolana16"
   - Hacer clic en "Actualizar"

3. **Probar la funcionalidad:**
   - Crear o editar una póliza
   - Intentar generar el PDF personalizado
   - Verificar que no aparezcan errores

## Troubleshooting

### Error: "Permission denied"

```bash
# Ejecutar como root
sudo python3 install_dependencies.py
# o
docker exec -u root -it <contenedor> python3 install_dependencies.py
```

### Error: "pip: command not found"

```bash
# Instalar pip primero
apt-get update && apt-get install -y python3-pip
```

### Error: "Module not found" después de instalar

```bash
# Verificar que las librerías se instalaron en el Python correcto
which python3
python3 -m pip list | grep -E "pypdf|PyPDF2|reportlab"

# Si no aparecen, reinstalar:
python3 -m pip install --force-reinstall pypdf PyPDF2 reportlab
```

### El módulo sigue fallando

1. Verificar los logs de Odoo:
   ```bash
   docker logs <nombre_contenedor>
   ```

2. Verificar que la versión del módulo se actualizó:
   - En Odoo: Aplicaciones → LaVenezolana16 → debe mostrar versión 16.0.2.18.0

3. Limpiar caché de Python:
   ```bash
   find . -name "__pycache__" -type d -exec rm -rf {} +
   find . -name "*.pyc" -delete
   ```

## Notas importantes

- **Persistencia:** Las dependencias instaladas con `pip` en un contenedor se perderán al recrear el contenedor. Para una solución permanente, modifica el Dockerfile.

- **Versiones:** El módulo está configurado para funcionar con múltiples versiones de las librerías PDF, por lo que debería funcionar incluso si algunas dependencias no se instalan.

- **Fallback:** Si las librerías especializadas fallan, el módulo intentará devolver la plantilla PDF original sin modificaciones.

- **Rendimiento:** `pypdf` es más moderna y eficiente que `PyPDF2`, pero ambas son compatibles.

## Contacto

Si sigues teniendo problemas después de seguir estas instrucciones, proporciona:

1. Versión de Odoo
2. Tipo de instalación (Docker, nativo, etc.)
3. Sistema operativo del contenedor
4. Logs completos del error
5. Resultado de `python3 --version` y `pip3 --version`