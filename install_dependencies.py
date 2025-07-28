#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar las dependencias necesarias para el procesamiento de PDF
Compatible con contenedores de Odoo que usan python3
"""

import subprocess
import sys
import os

def get_python_executable():
    """Encuentra el ejecutable de Python disponible"""
    # Intentar diferentes opciones de Python
    python_options = ['python3', 'python', '/usr/bin/python3', '/usr/local/bin/python3']
    
    for python_cmd in python_options:
        try:
            result = subprocess.run([python_cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"Usando Python: {python_cmd} ({result.stdout.strip()})")
                return python_cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    # Si no encuentra ninguno, usar sys.executable como fallback
    print(f"Usando Python por defecto: {sys.executable}")
    return sys.executable

def install_package(package, python_exec):
    """Instala un paquete usando pip"""
    try:
        # Intentar con pip3 primero, luego pip
        pip_commands = [f"{python_exec} -m pip", "pip3", "pip"]
        
        for pip_cmd in pip_commands:
            try:
                cmd = f"{pip_cmd} install {package}"
                result = subprocess.run(cmd.split(), 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print(f"✓ {package} instalado exitosamente con {pip_cmd}")
                    return True
                else:
                    print(f"Intento fallido con {pip_cmd}: {result.stderr}")
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"Error con {pip_cmd}: {e}")
                continue
        
        print(f"✗ No se pudo instalar {package} con ningún método")
        return False
        
    except Exception as e:
        print(f"✗ Error instalando {package}: {e}")
        return False

def main():
    """Función principal"""
    packages = [
        "pypdf",
        "PyPDF2", 
        "reportlab"
    ]
    
    print("=== Instalador de dependencias para procesamiento de PDF ===")
    print(f"Sistema operativo: {os.name}")
    
    # Encontrar el ejecutable de Python
    python_exec = get_python_executable()
    
    print(f"\nInstalando {len(packages)} paquetes...")
    
    success_count = 0
    for i, package in enumerate(packages, 1):
        print(f"\n[{i}/{len(packages)}] Instalando {package}...")
        if install_package(package, python_exec):
            success_count += 1
    
    print(f"\n=== Resumen de instalación ===")
    print(f"Paquetes instalados: {success_count}/{len(packages)}")
    
    if success_count == len(packages):
        print("¡Todas las dependencias se instalaron correctamente!")
        print("\nPuedes proceder a reiniciar Odoo y actualizar el módulo.")
    else:
        print("Algunas dependencias no se pudieron instalar.")
        print("El módulo funcionará con las librerías disponibles.")
        print("\nNota: En contenedores de Odoo, las dependencias pueden estar")
        print("preinstaladas o requerir instalación desde el Dockerfile.")

if __name__ == "__main__":
    main()