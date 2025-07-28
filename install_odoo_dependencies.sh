#!/bin/bash
# Script para instalar dependencias de PDF en contenedor de Odoo
# Compatible con contenedores Docker de Odoo

echo "=== Instalador de dependencias PDF para Odoo ==="
echo "Detectando entorno..."

# Verificar si estamos en un contenedor
if [ -f /.dockerenv ]; then
    echo "✓ Contenedor Docker detectado"
else
    echo "⚠ No se detectó contenedor Docker"
fi

# Verificar usuario
echo "Usuario actual: $(whoami)"
echo "Python disponible:"

# Buscar ejecutables de Python
for python_cmd in python3 python /usr/bin/python3 /usr/local/bin/python3; do
    if command -v $python_cmd >/dev/null 2>&1; then
        echo "  ✓ $python_cmd: $($python_cmd --version 2>&1)"
        PYTHON_CMD=$python_cmd
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "✗ No se encontró Python instalado"
    exit 1
fi

echo "\nUsando: $PYTHON_CMD"

# Verificar pip
echo "\nVerificando pip..."
for pip_cmd in "$PYTHON_CMD -m pip" pip3 pip; do
    if eval "$pip_cmd --version" >/dev/null 2>&1; then
        echo "  ✓ $pip_cmd disponible"
        PIP_CMD="$pip_cmd"
        break
    fi
done

if [ -z "$PIP_CMD" ]; then
    echo "✗ No se encontró pip instalado"
    echo "\nIntentando instalar pip..."
    
    # Intentar instalar pip
    if command -v apt-get >/dev/null 2>&1; then
        echo "Usando apt-get para instalar pip..."
        apt-get update && apt-get install -y python3-pip
    elif command -v yum >/dev/null 2>&1; then
        echo "Usando yum para instalar pip..."
        yum install -y python3-pip
    else
        echo "No se pudo instalar pip automáticamente"
        exit 1
    fi
    
    PIP_CMD="pip3"
fi

echo "\nUsando: $PIP_CMD"

# Instalar paquetes
packages=("pypdf" "PyPDF2" "reportlab")
success_count=0

echo "\n=== Instalando paquetes ==="
for package in "${packages[@]}"; do
    echo "\nInstalando $package..."
    
    if eval "$PIP_CMD install $package --no-cache-dir"; then
        echo "✓ $package instalado exitosamente"
        ((success_count++))
    else
        echo "✗ Error instalando $package"
        
        # Intentar con --user si falla
        echo "Intentando con --user..."
        if eval "$PIP_CMD install $package --user --no-cache-dir"; then
            echo "✓ $package instalado con --user"
            ((success_count++))
        else
            echo "✗ No se pudo instalar $package"
        fi
    fi
done

echo "\n=== Resumen ==="
echo "Paquetes instalados: $success_count/${#packages[@]}"

if [ $success_count -eq ${#packages[@]} ]; then
    echo "¡Todas las dependencias se instalaron correctamente!"
    echo "\nVerificando instalación..."
    
    for package in "${packages[@]}"; do
        if $PYTHON_CMD -c "import $package; print(f'✓ $package: {$package.__version__ if hasattr($package, '__version__') else 'OK'}')" 2>/dev/null; then
            echo "✓ $package importado correctamente"
        else
            echo "⚠ $package instalado pero no se puede importar"
        fi
    done
    
    echo "\n¡Listo! Puedes reiniciar Odoo y actualizar el módulo."
else
    echo "\nAlgunas dependencias no se pudieron instalar."
    echo "El módulo funcionará con las librerías disponibles."
    
    echo "\n=== Instrucciones manuales ==="
    echo "Si estás en un contenedor de Odoo, puedes intentar:"
    echo "1. Acceder como root: docker exec -u root -it <container_name> bash"
    echo "2. Instalar dependencias: apt-get update && apt-get install -y python3-pip"
    echo "3. Instalar paquetes: pip3 install pypdf PyPDF2 reportlab"
    echo "4. Reiniciar el contenedor"
fi

echo "\n=== Información del sistema ==="
echo "Distribución: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo 'Desconocida')"
echo "Python: $($PYTHON_CMD --version 2>&1)"
echo "Pip: $(eval "$PIP_CMD --version" 2>&1 | head -1)"
echo "Usuario: $(whoami)"
echo "Directorio: $(pwd)"

echo "\nScript completado."