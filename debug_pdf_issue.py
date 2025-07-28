#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para el problema de carga de datos en PDF
"""

import base64
import io
import os

# Intentar importar librerías PDF
try:
    from pypdf import PdfReader, PdfWriter
    PDF_LIBRARY = 'pypdf'
    print("✓ Usando pypdf")
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        PDF_LIBRARY = 'PyPDF2_new'
        print("✓ Usando PyPDF2 (nuevo)")
    except ImportError:
        try:
            from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter
            PDF_LIBRARY = 'PyPDF2_old'
            print("✓ Usando PyPDF2 (viejo)")
        except ImportError:
            print("✗ No se pudo importar ninguna librería PDF")
            exit(1)

def get_pdf_fields(pdf_path):
    """Extrae los campos de un archivo PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            
            fields = []
            
            if PDF_LIBRARY == 'pypdf':
                if hasattr(reader, 'get_fields') and reader.get_fields():
                    fields = list(reader.get_fields().keys())
            elif PDF_LIBRARY in ['PyPDF2_old', 'PyPDF2_new']:
                if hasattr(reader, 'getFields') and reader.getFields():
                    fields = list(reader.getFields().keys())
                elif hasattr(reader, 'get_fields') and reader.get_fields():
                    fields = list(reader.get_fields().keys())
            
            return fields
    except Exception as e:
        print(f"Error al leer PDF: {e}")
        return []

def test_pdf_filling(pdf_path, test_data):
    """Prueba el rellenado de PDF con datos de muestra"""
    try:
        print(f"\n=== PROBANDO RELLENADO DE PDF ===")
        print(f"Archivo: {pdf_path}")
        print(f"Librería: {PDF_LIBRARY}")
        
        with open(pdf_path, 'rb') as file:
            pdf_data = file.read()
        
        pdf_input = io.BytesIO(pdf_data)
        reader = PdfReader(pdf_input)
        writer = PdfWriter()
        
        # Copiar páginas
        for page in reader.pages:
            writer.add_page(page)
        
        fields_filled = 0
        errors = []
        
        # Intentar rellenar campos
        if PDF_LIBRARY == 'pypdf':
            if hasattr(reader, 'get_fields') and reader.get_fields():
                fields = reader.get_fields()
                print(f"Campos disponibles: {len(fields)}")
                
                for field_name, field_value in test_data.items():
                    if field_name in fields:
                        try:
                            writer.update_page_form_field_values(writer.pages[0], {field_name: str(field_value)})
                            print(f"✓ Campo '{field_name}' rellenado con: '{field_value}'")
                            fields_filled += 1
                        except Exception as e:
                            error_msg = f"✗ Error al rellenar campo '{field_name}': {str(e)}"
                            print(error_msg)
                            errors.append(error_msg)
                    else:
                        print(f"- Campo '{field_name}' no existe en PDF")
        
        elif PDF_LIBRARY in ['PyPDF2_old', 'PyPDF2_new']:
            if hasattr(reader, 'getFields') and reader.getFields():
                fields = reader.getFields()
                print(f"Campos disponibles: {len(fields)}")
                
                for field_name, field_value in test_data.items():
                    if field_name in fields:
                        try:
                            if hasattr(writer, 'updatePageFormFieldValues'):
                                writer.updatePageFormFieldValues(writer.getPage(0), {field_name: str(field_value)})
                            elif hasattr(writer, 'update_page_form_field_values'):
                                writer.update_page_form_field_values(writer.pages[0], {field_name: str(field_value)})
                            print(f"✓ Campo '{field_name}' rellenado con: '{field_value}'")
                            fields_filled += 1
                        except Exception as e:
                            error_msg = f"✗ Error al rellenar campo '{field_name}': {str(e)}"
                            print(error_msg)
                            errors.append(error_msg)
                    else:
                        print(f"- Campo '{field_name}' no existe en PDF")
        
        # Intentar generar PDF de salida
        try:
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            
            # Guardar PDF de prueba
            output_path = pdf_path.replace('.pdf', '_test_output.pdf')
            with open(output_path, 'wb') as f:
                f.write(output.getvalue())
            
            print(f"\n✓ PDF de prueba generado: {output_path}")
            print(f"✓ Campos rellenados exitosamente: {fields_filled}")
            
            if errors:
                print(f"\n⚠ Errores encontrados ({len(errors)}):")
                for error in errors:
                    print(f"  {error}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error al generar PDF de salida: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Error general en test_pdf_filling: {e}")
        return False

def main():
    # Ruta del PDF
    pdf_path = r"c:\Users\Usuario\Documents\Raul\odoo\LaVenezolana16\static\templates\LaVenezolanaCampos.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"✗ No se encontró el archivo PDF: {pdf_path}")
        return
    
    print(f"=== DIAGNÓSTICO DE PDF ===")
    print(f"Archivo: {pdf_path}")
    print(f"Tamaño: {os.path.getsize(pdf_path)} bytes")
    
    # Obtener campos del PDF
    fields = get_pdf_fields(pdf_path)
    print(f"\nCampos encontrados: {len(fields)}")
    
    if fields:
        print("\nLista de campos:")
        for i, field in enumerate(fields, 1):
            print(f"  {i:2d}. {field}")
    else:
        print("\n⚠ No se encontraron campos en el PDF")
        return
    
    # Datos de prueba basados en los campos reales del PDF
    test_data = {
        'numero_poliza': 'TEST-12345',
        'tomador_nombre': 'Juan Pérez de Prueba',
        'tomador_cedula': '12345678',
        'vigencia_desde': '01/01/2024',
        'vigencia_hasta': '31/12/2024',
        'marca_vehiculo': 'Toyota',
        'modelo_vehiculo': 'Corolla',
        'placa_vehiculo': 'ABC123',
        'ano': '2020',
        'color_vehiculo': 'Blanco',
        'serial_motor': 'MOT123456',
        'serial_carroceria': 'CAR789012',
        'exceso_limite': '50000',
        'danos_personas': '100000',
        'danos_cosas': '75000'
    }
    
    # Probar rellenado
    success = test_pdf_filling(pdf_path, test_data)
    
    if success:
        print("\n✓ Diagnóstico completado exitosamente")
    else:
        print("\n✗ Se encontraron problemas en el diagnóstico")

if __name__ == "__main__":
    main()