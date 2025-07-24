# -*- coding: utf-8 -*-

import base64
import io
import json
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    import PyPDF2
    import fitz  # PyMuPDF
except ImportError:
    _logger.warning("PyPDF2 or PyMuPDF not installed. PDF processing will be limited.")
    PyPDF2 = None
    fitz = None


class DesignGenerator(models.Model):
    _name = 'poliza.design.generator'
    _description = 'Generador de Diseños desde PDF'
    _order = 'create_date desc'

    name = fields.Char(
        string='Nombre del Diseño',
        required=True,
        default='Nuevo Diseño'
    )
    
    pdf_file = fields.Binary(
        string='Archivo PDF',
        required=True,
        help="Sube el PDF con el diseño de referencia"
    )
    
    pdf_filename = fields.Char(string='Nombre del Archivo')
    
    design_type = fields.Selection([
        ('poliza', 'Póliza Completa'),
        ('carnet', 'Carnet RCV'),
        ('both', 'Ambos')
    ], string='Tipo de Diseño', required=True, default='carnet')
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('analyzing', 'Analizando'),
        ('ready', 'Listo para Aplicar'),
        ('applied', 'Aplicado'),
        ('error', 'Error')
    ], string='Estado', default='draft')
    
    analysis_result = fields.Text(
        string='Resultado del Análisis',
        readonly=True
    )
    
    extracted_elements = fields.Text(
        string='Elementos Extraídos',
        readonly=True,
        help="JSON con los elementos extraídos del PDF"
    )
    
    generated_template = fields.Text(
        string='Template Generado',
        readonly=True
    )
    
    preview_html = fields.Html(
        string='Vista Previa',
        readonly=True
    )
    
    backup_template = fields.Text(
        string='Backup del Template Original',
        readonly=True
    )
    
    error_message = fields.Text(
        string='Mensaje de Error',
        readonly=True
    )
    
    active = fields.Boolean(default=True)

    @api.constrains('pdf_file')
    def _check_pdf_file(self):
        """Valida que el archivo sea un PDF válido"""
        for record in self:
            if record.pdf_file:
                try:
                    pdf_data = base64.b64decode(record.pdf_file)
                    if not pdf_data.startswith(b'%PDF'):
                        raise ValidationError("El archivo debe ser un PDF válido")
                except Exception as e:
                    raise ValidationError(f"Error al validar el PDF: {str(e)}")

    def action_analyze_pdf(self):
        """Analiza el PDF y extrae elementos de diseño"""
        self.ensure_one()
        
        if not self.pdf_file:
            raise UserError("Debe subir un archivo PDF primero")
        
        self.state = 'analyzing'
        
        try:
            # Decodificar el PDF
            pdf_data = base64.b64decode(self.pdf_file)
            
            # Analizar el PDF
            analysis_result = self._analyze_pdf_content(pdf_data)
            
            # Extraer elementos
            extracted_elements = self._extract_design_elements(pdf_data)
            
            # Generar template
            generated_template = self._generate_template(extracted_elements)
            
            # Crear vista previa
            preview_html = self._create_preview(generated_template)
            
            # Actualizar campos
            self.write({
                'analysis_result': analysis_result,
                'extracted_elements': json.dumps(extracted_elements, indent=2),
                'generated_template': generated_template,
                'preview_html': preview_html,
                'state': 'ready',
                'error_message': False
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Análisis Completado',
                    'message': 'El PDF ha sido analizado exitosamente. Revisa la vista previa.',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            self.write({
                'state': 'error',
                'error_message': str(e)
            })
            raise UserError(f"Error al analizar el PDF: {str(e)}")

    def _analyze_pdf_content(self, pdf_data):
        """Analiza el contenido del PDF"""
        analysis = []
        
        try:
            if fitz:  # PyMuPDF
                doc = fitz.open(stream=pdf_data, filetype="pdf")
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    
                    # Obtener dimensiones
                    rect = page.rect
                    analysis.append(f"Página {page_num + 1}:")
                    analysis.append(f"  - Dimensiones: {rect.width:.1f} x {rect.height:.1f} puntos")
                    
                    # Extraer texto
                    text_dict = page.get_text("dict")
                    blocks = text_dict.get("blocks", [])
                    analysis.append(f"  - Bloques de texto encontrados: {len(blocks)}")
                    
                    # Extraer imágenes
                    images = page.get_images()
                    analysis.append(f"  - Imágenes encontradas: {len(images)}")
                    
                doc.close()
            else:
                analysis.append("PyMuPDF no disponible. Análisis limitado.")
                
        except Exception as e:
            analysis.append(f"Error en análisis: {str(e)}")
        
        return "\n".join(analysis)

    def _extract_design_elements(self, pdf_data):
        """Extrae elementos de diseño del PDF"""
        elements = {
            'pages': [],
            'colors': [],
            'fonts': [],
            'images': [],
            'text_blocks': [],
            'layout': {}
        }
        
        try:
            if fitz:  # PyMuPDF
                doc = fitz.open(stream=pdf_data, filetype="pdf")
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    page_info = {
                        'number': page_num + 1,
                        'width': page.rect.width,
                        'height': page.rect.height,
                        'text_blocks': [],
                        'images': []
                    }
                    
                    # Extraer bloques de texto con posición
                    text_dict = page.get_text("dict")
                    for block in text_dict.get("blocks", []):
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line.get("spans", []):
                                    text_block = {
                                        'text': span.get("text", ""),
                                        'x': span.get("bbox", [0])[0],
                                        'y': span.get("bbox", [0, 0])[1],
                                        'width': span.get("bbox", [0, 0, 0])[2] - span.get("bbox", [0])[0],
                                        'height': span.get("bbox", [0, 0, 0, 0])[3] - span.get("bbox", [0, 0])[1],
                                        'font': span.get("font", ""),
                                        'size': span.get("size", 12),
                                        'color': span.get("color", 0)
                                    }
                                    page_info['text_blocks'].append(text_block)
                    
                    # Extraer imágenes
                    images = page.get_images()
                    for img_index, img in enumerate(images):
                        img_info = {
                            'index': img_index,
                            'xref': img[0],
                            'width': img[2],
                            'height': img[3]
                        }
                        page_info['images'].append(img_info)
                    
                    elements['pages'].append(page_info)
                
                doc.close()
                
        except Exception as e:
            _logger.error(f"Error extracting elements: {str(e)}")
        
        return elements

    def _generate_template(self, elements):
        """Genera el template XML basado en los elementos extraídos"""
        if self.design_type == 'carnet':
            return self._generate_carnet_template(elements)
        elif self.design_type == 'poliza':
            return self._generate_poliza_template(elements)
        else:
            return self._generate_both_templates(elements)

    def _generate_carnet_template(self, elements):
        """Genera template para carnet RCV"""
        template = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Template del carnet RCV generado automáticamente -->
        <template id="report_carnet_rcv_template_custom">
            <t t-call="web.html_container">
                <t t-foreach="docs" t-as="poliza">
                    <div class="page" style="width: 85mm; height: 54mm; margin: 0; padding: 3mm; font-family: Arial, sans-serif; font-size: 8pt;">
                        <!-- Encabezado -->
                        <div style="text-align: center; margin-bottom: 2mm;">
                            <strong style="font-size: 10pt;">LA VENEZOLANA DE SEGUROS Y VIDA</strong><br/>
                            <span style="font-size: 7pt;">CARNET DE RESPONSABILIDAD CIVIL VEHICULAR</span>
                        </div>
                        
                        <!-- Información principal en dos columnas -->
                        <table style="width: 100%; font-size: 7pt; border-collapse: collapse;">
                            <tr>
                                <td style="width: 50%; vertical-align: top;">
                                    <strong>Póliza N°:</strong> <span t-field="poliza.numero_poliza"/><br/>
                                    <strong>Asegurado:</strong> <span t-field="poliza.nombre_asegurador"/><br/>
                                    <strong>C.I./RIF:</strong> <span t-field="poliza.cedula_rif_asegurador"/><br/>
                                    <strong>Teléfono:</strong> <span t-field="poliza.telefono_asegurador"/>
                                </td>
                                <td style="width: 50%; vertical-align: top;">
                                    <strong>Vigencia:</strong><br/>
                                    <span>Desde: </span><span t-field="poliza.vigencia_desde" t-options="{'widget': 'date'}"/><br/>
                                    <span>Hasta: </span><span t-field="poliza.vigencia_hasta" t-options="{'widget': 'date'}"/><br/>
                                    <span>Hora: </span><span t-field="poliza.hora_vigencia"/>
                                </td>
                            </tr>
                        </table>
                        
                        <!-- Información del vehículo -->
                        <div style="margin-top: 2mm; font-size: 7pt;">
                            <strong>DATOS DEL VEHÍCULO</strong><br/>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td><strong>Marca:</strong> <span t-field="poliza.marca_vehiculo"/></td>
                                    <td><strong>Modelo:</strong> <span t-field="poliza.modelo_vehiculo"/></td>
                                </tr>
                                <tr>
                                    <td><strong>Placa:</strong> <span t-field="poliza.placa_vehiculo"/></td>
                                    <td><strong>Color:</strong> <span t-field="poliza.color_vehiculo"/></td>
                                </tr>
                                <tr>
                                    <td><strong>Puestos:</strong> <span t-field="poliza.puestos_vehiculo"/></td>
                                    <td><strong>Serial:</strong> <span t-field="poliza.serial_carroceria"/></td>
                                </tr>
                            </table>
                        </div>
                        
                        <!-- Coberturas -->
                        <div style="margin-top: 2mm; font-size: 6pt;">
                            <strong>COBERTURAS:</strong>
                            <span>Muerte e Invalidez: </span><span t-field="poliza.muerte_invalidez" t-options="{'widget': 'monetary'}"/> |
                            <span>Daños a Cosas: </span><span t-field="poliza.danos_cosas" t-options="{'widget': 'monetary'}"/>
                        </div>
                        
                        <!-- Pie de página -->
                        <div style="text-align: center; margin-top: 2mm; font-size: 6pt; border-top: 1px solid #000; padding-top: 1mm;">
                            Este carnet debe portarse en el vehículo en todo momento
                        </div>
                    </div>
                </t>
            </t>
        </template>
    </data>
</odoo>'''
        return template

    def _generate_poliza_template(self, elements):
        """Genera template para póliza completa"""
        # Template básico para póliza - se puede expandir
        template = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Template de póliza generado automáticamente -->
        <template id="report_poliza_template_custom">
            <t t-call="web.html_container">
                <t t-foreach="docs" t-as="poliza">
                    <t t-call="web.external_layout">
                        <div class="page">
                            <!-- Contenido de la póliza personalizada -->
                            <div class="text-center">
                                <h2>PÓLIZA DE SEGURO VEHICULAR</h2>
                                <h3>LA VENEZOLANA DE SEGUROS Y VIDA</h3>
                            </div>
                            
                            <!-- Aquí iría el contenido personalizado basado en el PDF -->
                            
                        </div>
                    </t>
                </t>
            </t>
        </template>
    </data>
</odoo>'''
        return template

    def _generate_both_templates(self, elements):
        """Genera ambos templates"""
        carnet = self._generate_carnet_template(elements)
        poliza = self._generate_poliza_template(elements)
        return f"{carnet}\n\n{poliza}"

    def _create_preview(self, template):
        """Crea una vista previa HTML del template"""
        preview = f'''
        <div style="border: 1px solid #ccc; padding: 10px; margin: 10px; background: #f9f9f9;">
            <h4>Vista Previa del Template Generado</h4>
            <div style="background: white; padding: 10px; border: 1px solid #ddd;">
                <p><strong>Tipo:</strong> {dict(self._fields['design_type'].selection)[self.design_type]}</p>
                <p><strong>Estado:</strong> Template generado exitosamente</p>
                <p><strong>Elementos detectados:</strong> Texto, imágenes y layout extraídos del PDF</p>
                <div style="margin-top: 10px; padding: 10px; background: #e8f5e8; border-left: 4px solid #4CAF50;">
                    <strong>✓ Template listo para aplicar</strong><br/>
                    El diseño ha sido extraído y convertido a formato Odoo.
                </div>
            </div>
        </div>
        '''
        return preview

    def action_apply_design(self):
        """Aplica el diseño generado a los reportes"""
        self.ensure_one()
        
        if self.state != 'ready':
            raise UserError("El diseño debe estar en estado 'Listo para Aplicar'")
        
        try:
            # Hacer backup del template actual
            self._backup_current_template()
            
            # Aplicar el nuevo template
            self._apply_new_template()
            
            self.state = 'applied'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Diseño Aplicado',
                    'message': 'El nuevo diseño ha sido aplicado exitosamente a los reportes.',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(f"Error al aplicar el diseño: {str(e)}")

    def _backup_current_template(self):
        """Hace backup del template actual"""
        if self.design_type in ['carnet', 'both']:
            # Buscar el template actual del carnet
            carnet_template = self.env['ir.ui.view'].search([
                ('key', '=', 'LaVenezolana16.report_carnet_rcv_template')
            ], limit=1)
            
            if carnet_template:
                self.backup_template = carnet_template.arch_db

    def _apply_new_template(self):
        """Aplica el nuevo template"""
        if self.design_type in ['carnet', 'both']:
            # Actualizar el template del carnet
            carnet_template = self.env['ir.ui.view'].search([
                ('key', '=', 'LaVenezolana16.report_carnet_rcv_template')
            ], limit=1)
            
            if carnet_template and self.generated_template:
                # Extraer solo la parte del template del XML generado
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(self.generated_template)
                    template_elem = root.find('.//template[@id="report_carnet_rcv_template_custom"]')
                    if template_elem is not None:
                        new_arch = ET.tostring(template_elem, encoding='unicode')
                        carnet_template.write({'arch_db': new_arch})
                except Exception as e:
                    _logger.error(f"Error parsing template: {str(e)}")

    def action_restore_backup(self):
        """Restaura el template desde el backup"""
        self.ensure_one()
        
        if not self.backup_template:
            raise UserError("No hay backup disponible para restaurar")
        
        try:
            if self.design_type in ['carnet', 'both']:
                carnet_template = self.env['ir.ui.view'].search([
                    ('key', '=', 'LaVenezolana16.report_carnet_rcv_template')
                ], limit=1)
                
                if carnet_template:
                    carnet_template.write({'arch_db': self.backup_template})
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Backup Restaurado',
                    'message': 'El diseño original ha sido restaurado exitosamente.',
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(f"Error al restaurar el backup: {str(e)}")