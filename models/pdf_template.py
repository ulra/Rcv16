# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import io
import logging

_logger = logging.getLogger(__name__)

# Intentar importar librerías de PDF en orden de preferencia
try:
    import pypdf
    from pypdf import PdfReader, PdfWriter
    PDF_LIBRARY = 'pypdf'
    _logger.info("Usando pypdf para procesamiento de PDF")
except ImportError:
    try:
        import PyPDF2
        from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter
        PDF_LIBRARY = 'PyPDF2_old'
        _logger.info("Usando PyPDF2 (versión antigua) para procesamiento de PDF")
    except ImportError:
        try:
            from PyPDF2 import PdfReader, PdfWriter
            PDF_LIBRARY = 'PyPDF2_new'
            _logger.info("Usando PyPDF2 (versión nueva) para procesamiento de PDF")
        except ImportError:
            _logger.error("No se pudo importar ninguna librería de PDF")
            PDF_LIBRARY = None

import traceback
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class PdfTemplate(models.Model):
    _name = 'pdf.template'
    _description = 'Plantilla PDF para Pólizas'
    _order = 'name'

    name = fields.Char(
        string='Nombre de la Plantilla',
        required=True
    )
    
    template_file = fields.Binary(
        string='Archivo PDF Template',
        required=True,
        help="Sube aquí tu plantilla PDF con campos de formulario"
    )
    
    template_filename = fields.Char(
        string='Nombre del Archivo'
    )
    
    description = fields.Text(
        string='Descripción'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    is_default = fields.Boolean(
        string='Plantilla por Defecto',
        help="Marca esta plantilla como la predeterminada para nuevas pólizas"
    )

    @api.model
    def create(self, vals):
        """Al crear una nueva plantilla por defecto, desmarcar las demás"""
        if vals.get('is_default'):
            self.search([('is_default', '=', True)]).write({'is_default': False})
        return super().create(vals)

    def write(self, vals):
        """Al marcar como defecto, desmarcar las demás"""
        if vals.get('is_default'):
            self.search([('is_default', '=', True), ('id', '!=', self.id)]).write({'is_default': False})
        return super().write(vals)

    def get_pdf_fields(self):
        """
        Obtiene la lista de campos disponibles en la plantilla PDF
        """
        try:
            pdf_data = base64.b64decode(self.template_file)
            pdf_input = io.BytesIO(pdf_data)
            reader = PdfReader(pdf_input)
            
            fields = []
            fields_info = {}
            
            if PDF_LIBRARY == 'pypdf':
                if hasattr(reader, 'get_fields') and reader.get_fields():
                    fields_dict = reader.get_fields()
                    fields = list(fields_dict.keys())
                    fields_info = fields_dict
            elif PDF_LIBRARY in ['PyPDF2_old', 'PyPDF2_new']:
                if hasattr(reader, 'getFields') and reader.getFields():
                    fields_dict = reader.getFields()
                    fields = list(fields_dict.keys())
                    fields_info = fields_dict
                elif hasattr(reader, 'get_fields') and reader.get_fields():
                    fields_dict = reader.get_fields()
                    fields = list(fields_dict.keys())
                    fields_info = fields_dict
            
            _logger.info(f"Campos encontrados en PDF: {fields}")
            if fields_info:
                for field_name, field_obj in fields_info.items():
                    _logger.info(f"Campo '{field_name}': {type(field_obj)}")
            
            return fields
        except Exception as e:
            _logger.error(f"Error al obtener campos del PDF: {str(e)}")
            return []
    
    def debug_pdf_fields(self):
        """
        Método para debuggear los campos del PDF desde la interfaz
        """
        if not self.template_file:
            raise UserError("No hay archivo de plantilla cargado")
        
        fields = self.get_pdf_fields()
        
        if not fields:
            message = "No se encontraron campos de formulario en este PDF.\n\nEsto puede significar que:\n- El PDF no tiene campos rellenables\n- Los campos están protegidos\n- El PDF está dañado"
        else:
            message = f"Campos encontrados en el PDF ({len(fields)}):\n\n"
            for i, field in enumerate(fields, 1):
                message += f"{i}. {field}\n"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Campos del PDF',
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def test_pdf_mapping(self):
        """
        Método de prueba para verificar el mapeo entre datos y campos PDF
        """
        if not self.template_file:
            raise UserError("No hay archivo de plantilla cargado")
        
        # Obtener campos del PDF
        pdf_fields = self.get_pdf_fields()
        
        # Simular datos de póliza típicos
        sample_data = {
            'numero_poliza': '12345',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-12-31',
            'tomador_nombre': 'Juan Pérez',
            'tomador_cedula': '12345678',
            'vehiculo_placa': 'ABC123',
            'vehiculo_marca': 'Toyota',
            'vehiculo_modelo': 'Corolla',
            'vehiculo_año': '2020',
            'suma_asegurada': '50000.00',
            'prima_total': '1500.00'
        }
        
        # Analizar coincidencias
        matching_fields = []
        missing_in_pdf = []
        unused_pdf_fields = list(pdf_fields)
        
        for data_field in sample_data.keys():
            if data_field in pdf_fields:
                matching_fields.append(data_field)
                if data_field in unused_pdf_fields:
                    unused_pdf_fields.remove(data_field)
            else:
                missing_in_pdf.append(data_field)
        
        # Crear mensaje de diagnóstico
        message = f"DIAGNÓSTICO DE MAPEO PDF\n\n"
        message += f"📋 Campos en PDF: {len(pdf_fields)}\n"
        message += f"📊 Datos de muestra: {len(sample_data)}\n"
        message += f"✅ Coincidencias: {len(matching_fields)}\n\n"
        
        if matching_fields:
            message += f"CAMPOS QUE COINCIDEN ({len(matching_fields)}):\n"
            for field in matching_fields:
                message += f"• {field}\n"
            message += "\n"
        
        if missing_in_pdf:
            message += f"DATOS SIN CAMPO EN PDF ({len(missing_in_pdf)}):\n"
            for field in missing_in_pdf:
                message += f"• {field}\n"
            message += "\n"
        
        if unused_pdf_fields:
            message += f"CAMPOS PDF SIN DATOS ({len(unused_pdf_fields)}):\n"
            for field in unused_pdf_fields:
                message += f"• {field}\n"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Diagnóstico de Mapeo PDF',
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }

    def fill_pdf_template(self, poliza_data):
        """
        Rellena la plantilla PDF con los datos de la póliza
        """
        try:
            _logger.info(f"Iniciando rellenado de PDF con librería: {PDF_LIBRARY}")
            _logger.info(f"Datos recibidos ({len(poliza_data)} campos): {list(poliza_data.keys())}")
            
            # Obtener campos disponibles en el PDF
            available_fields = self.get_pdf_fields()
            _logger.info(f"Campos disponibles en PDF ({len(available_fields)}): {available_fields}")
            
            # Verificar coincidencias entre datos y campos
            matching_fields = [field for field in poliza_data.keys() if field in available_fields]
            _logger.info(f"Campos que coinciden ({len(matching_fields)}): {matching_fields}")
            
            if not available_fields:
                _logger.warning("No se encontraron campos de formulario en el PDF. El PDF podría no tener campos rellenables.")
                return self._generate_simple_pdf(poliza_data)
            
            if not matching_fields:
                _logger.warning("Ningún campo de datos coincide con los campos del PDF.")
                _logger.info("Datos disponibles: " + ", ".join(poliza_data.keys()))
                _logger.info("Campos PDF: " + ", ".join(available_fields))
            
            pdf_data = base64.b64decode(self.template_file)
            pdf_input = io.BytesIO(pdf_data)
            reader = PdfReader(pdf_input)
            writer = PdfWriter()
            
            # Copiar todas las páginas
            for page in reader.pages:
                writer.add_page(page)
            
            fields_filled = 0
            
            # Intentar rellenar campos según la librería disponible
            if PDF_LIBRARY == 'pypdf':
                # Usar pypdf (más moderno)
                if hasattr(reader, 'get_fields') and reader.get_fields():
                    fields = reader.get_fields()
                    
                    # Rellenar campos
                    for field_name, field_value in poliza_data.items():
                        if field_name in fields:
                            try:
                                writer.update_page_form_field_values(writer.pages[0], {field_name: str(field_value)})
                                _logger.info(f"✓ Campo '{field_name}' rellenado con: '{field_value}'")
                                fields_filled += 1
                            except Exception as e:
                                _logger.warning(f"✗ Error al rellenar campo '{field_name}': {str(e)}")
                        else:
                            _logger.debug(f"- Campo '{field_name}' no existe en PDF")
                            
            elif PDF_LIBRARY in ['PyPDF2_old', 'PyPDF2_new']:
                # Usar PyPDF2
                if hasattr(reader, 'getFields') and reader.getFields():
                    fields = reader.getFields()
                    
                    # Rellenar campos
                    for field_name, field_value in poliza_data.items():
                        if field_name in fields:
                            try:
                                if hasattr(writer, 'updatePageFormFieldValues'):
                                    writer.updatePageFormFieldValues(writer.getPage(0), {field_name: str(field_value)})
                                elif hasattr(writer, 'update_page_form_field_values'):
                                    writer.update_page_form_field_values(writer.pages[0], {field_name: str(field_value)})
                                _logger.info(f"✓ Campo '{field_name}' rellenado con: '{field_value}'")
                                fields_filled += 1
                            except Exception as e:
                                _logger.warning(f"✗ Error al rellenar campo '{field_name}': {str(e)}")
                        else:
                            _logger.debug(f"- Campo '{field_name}' no existe en PDF")
            
            _logger.info(f"Resumen: {fields_filled} campos rellenados de {len(matching_fields)} coincidencias")
            
            # Generar PDF final
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            
            _logger.info("PDF procesado exitosamente")
            return output.getvalue()
            
        except Exception as e:
            _logger.error(f"Error al rellenar PDF: {str(e)}")
            
            # Fallback: generar PDF simple con reportlab
            try:
                _logger.info("Intentando generar PDF simple como fallback")
                return self._generate_simple_pdf(poliza_data)
            except Exception as fallback_error:
                _logger.error(f"Error en fallback: {str(fallback_error)}")
                # Último recurso: devolver plantilla original
                _logger.warning("Devolviendo plantilla original sin modificar")
                return base64.b64decode(self.template_file)
    
    def _generate_simple_pdf(self, poliza_data):
        """
        Genera un PDF simple usando reportlab con los datos de la póliza
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            
            # Título
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, height - 50, "PÓLIZA DE SEGURO")
            
            # Datos de la póliza
            y_position = height - 100
            p.setFont("Helvetica", 12)
            
            for key, value in poliza_data.items():
                if y_position < 50:  # Nueva página si es necesario
                    p.showPage()
                    y_position = height - 50
                
                text = f"{key}: {value}"
                p.drawString(50, y_position, text)
                y_position -= 20
            
            p.save()
            buffer.seek(0)
            result = buffer.getvalue()
            
            _logger.info(f"PDF simple generado exitosamente, tamaño: {len(result)} bytes")
            return result
            
        except Exception as e:
            _logger.error(f"Error al generar PDF simple: {str(e)}")
            raise UserError(f"Error crítico al generar PDF: {str(e)}")