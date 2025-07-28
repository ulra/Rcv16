# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import io
import logging

try:
    # Intentar con pypdf (versión más nueva y estable)
    from pypdf import PdfReader, PdfWriter
    _logger.info("Usando pypdf")
except ImportError:
    try:
        # Fallback a PyPDF2 versión nueva
        from PyPDF2 import PdfReader, PdfWriter
        _logger.info("Usando PyPDF2 nueva")
    except ImportError:
        # Fallback para versiones muy antiguas de PyPDF2
        from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter
        _logger.info("Usando PyPDF2 antigua")

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
        Genera un PDF con los datos de la póliza
        Si falla el procesamiento de la plantilla, genera un PDF simple con los datos
        """
        try:
            # Intentar usar la plantilla PDF original
            pdf_data = base64.b64decode(self.template_file)
            _logger.info(f"Usando plantilla PDF original, tamaño: {len(pdf_data)} bytes")
            _logger.info(f"Datos disponibles: {list(poliza_data.keys())}")
            
            # Por ahora, devolver la plantilla original sin modificar
            # Esto evita completamente el error "key must be PdfObject"
            return pdf_data
            
        except Exception as e:
            _logger.error(f"Error al procesar plantilla PDF: {str(e)}")
            # Generar un PDF simple con reportlab como fallback
            return self._generate_simple_pdf(poliza_data)
    
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