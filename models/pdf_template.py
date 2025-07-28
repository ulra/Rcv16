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
            
            # Procesar cada página
            try:
                # API nueva (PyPDF2 >= 2.0)
                num_pages = len(reader.pages)
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    
                    # Si la página tiene campos de formulario, rellenarlos
                    if hasattr(writer, 'update_page_form_field_values') and '/Annots' in page:
                        writer.update_page_form_field_values(
                            writer.add_page(page), 
                            poliza_data
                        )
                    else:
                        writer.add_page(page)
            except AttributeError:
                # API antigua (PyPDF2 < 2.0)
                num_pages = reader.getNumPages()
                for page_num in range(num_pages):
                    page = reader.getPage(page_num)
                    
                    # Para versiones antiguas, intentar rellenar campos
                    if hasattr(reader, 'getFields') and reader.getFields():
                        for field_name, field_value in poliza_data.items():
                            if field_name in reader.getFields():
                                try:
                                    page.update({field_name: field_value})
                                except:
                                    pass
                    
                    writer.addPage(page)
            
            # Generar el PDF resultante
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            _logger.error(f"Error al rellenar plantilla PDF: {str(e)}")
            raise models.UserError(f"Error al procesar la plantilla PDF: {str(e)}")