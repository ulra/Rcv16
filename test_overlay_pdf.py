#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la funcionalidad de overlay PDF
"""

import sys
import os
import base64
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def test_overlay_pdf():
    """
    Prueba la funcionalidad de overlay PDF
    """
    print("🔍 Iniciando prueba de overlay PDF...")
    
    # Ruta del PDF template
    template_path = "static/templates/LaVenezolanaCampos.pdf"
    
    if not os.path.exists(template_path):
        print(f"❌ Error: No se encuentra el archivo {template_path}")
        return False
    
    try:
        # Datos de prueba
        poliza_data = {
            'numero_poliza': '12345678',
            'tomador_nombre': 'Juan Pérez',
            'tomador_cedula': '12345678',
            'vigencia_desde': '01/01/2024',
            'vigencia_hasta': '01/01/2025',
            'marca_vehiculo': 'Toyota',
            'modelo_vehiculo': 'Corolla',
            'placa_vehiculo': 'ABC123',
            'ano': '2020',
            'color_vehiculo': 'Blanco',
            'serial_motor': 'MOT123456',
            'serial_carroceria': 'CAR789012',
            'exceso_limite': '500.00',
            'danos_personas': '1000000.00',
            'danos_cosas': '500000.00',
        }
        
        print(f"📄 Procesando template: {template_path}")
        print(f"📊 Datos de prueba: {len(poliza_data)} campos")
        
        # Crear overlay con los datos
        overlay_buffer = io.BytesIO()
        p = canvas.Canvas(overlay_buffer, pagesize=letter)
        
        # Configurar fuente
        p.setFont("Helvetica", 10)
        
        # Posiciones para los campos
        field_positions = {
            'numero_poliza': (150, 720),
            'tomador_nombre': (150, 680),
            'tomador_cedula': (400, 680),
            'vigencia_desde': (150, 640),
            'vigencia_hasta': (400, 640),
            'marca_vehiculo': (150, 600),
            'modelo_vehiculo': (300, 600),
            'placa_vehiculo': (450, 600),
            'ano': (150, 560),
            'color_vehiculo': (250, 560),
            'serial_motor': (150, 520),
            'serial_carroceria': (350, 520),
            'exceso_limite': (150, 480),
            'danos_personas': (300, 480),
            'danos_cosas': (450, 480),
        }
        
        # Dibujar los datos en las posiciones
        fields_drawn = 0
        for field_name, field_value in poliza_data.items():
            if field_value and field_name in field_positions:
                x, y = field_positions[field_name]
                p.drawString(x, y, str(field_value))
                print(f"✓ Campo '{field_name}' dibujado en ({x}, {y}): '{field_value}'")
                fields_drawn += 1
        
        p.save()
        overlay_buffer.seek(0)
        
        # Leer template original
        with open(template_path, 'rb') as f:
            template_data = f.read()
        
        template_buffer = io.BytesIO(template_data)
        template_reader = PdfReader(template_buffer)
        overlay_reader = PdfReader(overlay_buffer)
        writer = PdfWriter()
        
        # Superponer en cada página
        for i, page in enumerate(template_reader.pages):
            if i < len(overlay_reader.pages):
                page.merge_page(overlay_reader.pages[i])
            writer.add_page(page)
        
        # Generar PDF final
        output_path = "static/templates/LaVenezolanaCampos_overlay_test.pdf"
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        print(f"✅ PDF con overlay generado exitosamente: {output_path}")
        print(f"📊 Campos superpuestos: {fields_drawn}/{len(poliza_data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando prueba de overlay PDF")
    print("=" * 50)
    
    success = test_overlay_pdf()
    
    print("=" * 50)
    if success:
        print("✅ Prueba completada exitosamente")
        print("\n📋 Próximos pasos:")
        print("1. Reiniciar Odoo")
        print("2. Actualizar el módulo a versión 16.0.2.28.0")
        print("3. Probar generar PDF desde una póliza")
        print("4. Verificar que los datos aparezcan en el PDF")
    else:
        print("❌ La prueba falló")
        print("\n🔧 Verificar:")
        print("1. Que el archivo LaVenezolanaCampos.pdf existe")
        print("2. Que las librerías pypdf y reportlab están instaladas")
        print("3. Permisos de escritura en el directorio")