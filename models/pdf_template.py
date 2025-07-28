# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import io
import logging
try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    # Fallback para versiones antiguas de PyPDF2
    from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

_logger = logging.getLogger(__name__)


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
            if hasattr(reader, 'get_fields') and reader.get_fields():
                fields = list(reader.get_fields().keys())
            elif hasattr(reader, 'getFields') and reader.getFields():
                fields = list(reader.getFields().keys())
            
            return fields
        except Exception as e:
            _logger.error(f"Error al obtener campos del PDF: {str(e)}")
            return []

    def fill_pdf_template(self, poliza_data):
        """
        Rellena la plantilla PDF con los datos de la póliza
        """
        try:
            # Decodificar el archivo PDF
            pdf_data = base64.b64decode(self.template_file)
            pdf_input = io.BytesIO(pdf_data)
            
            # Leer el PDF template
            reader = PdfReader(pdf_input)
            writer = PdfWriter()
            
            # Log de campos disponibles para depuración
            available_fields = self.get_pdf_fields()
            _logger.info(f"Campos disponibles en PDF: {available_fields}")
            _logger.info(f"Datos a rellenar: {list(poliza_data.keys())}")
            
            # Copiar todas las páginas primero
            if hasattr(reader, 'pages'):
                # API nueva (PyPDF2 >= 3.0)
                for page in reader.pages:
                    writer.add_page(page)
            else:
                # API antigua (PyPDF2 < 3.0)
                for page_num in range(reader.getNumPages()):
                    writer.addPage(reader.getPage(page_num))
            
            # Intentar rellenar campos de formulario
            try:
                # Obtener campos disponibles
                pdf_fields = None
                if hasattr(reader, 'get_fields'):
                    pdf_fields = reader.get_fields()
                elif hasattr(reader, 'getFields'):
                    pdf_fields = reader.getFields()
                
                if pdf_fields:
                    _logger.info(f"Campos encontrados en PDF: {list(pdf_fields.keys())}")
                    
                    # Preparar datos para rellenar (solo campos que existen)
                    fields_to_fill = {}
                    for field_name, field_value in poliza_data.items():
                        if field_name in pdf_fields:
                            fields_to_fill[field_name] = str(field_value) if field_value is not None else ''
                    
                    _logger.info(f"Campos a rellenar: {list(fields_to_fill.keys())}")
                    
                    # Rellenar campos usando el método más compatible
                    if fields_to_fill:
                        if hasattr(writer, 'update_page_form_field_values'):
                            # API nueva
                            try:
                                writer.update_page_form_field_values(writer.pages[0], fields_to_fill)
                            except Exception as e:
                                _logger.warning(f"Error con update_page_form_field_values: {e}")
                                # Intentar campo por campo
                                for field_name, field_value in fields_to_fill.items():
                                    try:
                                        writer.update_page_form_field_values(
                                            writer.pages[0], {field_name: field_value}
                                        )
                                    except Exception as field_error:
                                        _logger.warning(f"No se pudo rellenar {field_name}: {field_error}")
                        elif hasattr(writer, 'updatePageFormFieldValues'):
                            # API antigua
                            try:
                                writer.updatePageFormFieldValues(writer.getPage(0), fields_to_fill)
                            except Exception as e:
                                _logger.warning(f"Error con updatePageFormFieldValues: {e}")
                else:
                    _logger.warning("No se encontraron campos de formulario en el PDF")
                    
            except Exception as form_error:
                _logger.error(f"Error al rellenar campos de formulario: {form_error}")
                # Continuar sin rellenar campos
            
            # Generar el PDF resultante
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            _logger.error(f"Error al rellenar plantilla PDF: {str(e)}")
            raise models.UserError(f"Error al procesar la plantilla PDF: {str(e)}")