# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class DesignGeneratorWizard(models.TransientModel):
    _name = 'poliza.design.generator.wizard'
    _description = 'Asistente para Generador de Diseños'

    name = fields.Char(
        string='Nombre del Diseño',
        required=True,
        default='Diseño Personalizado'
    )
    
    design_type = fields.Selection([
        ('carnet', 'Carnet RCV'),
        ('poliza', 'Póliza Completa'),
        ('both', 'Ambos')
    ], string='Tipo de Diseño', required=True, default='carnet')
    
    pdf_file = fields.Binary(
        string='Archivo PDF de Referencia',
        required=True,
        help="Sube el PDF con el diseño que quieres replicar"
    )
    
    pdf_filename = fields.Char(string='Nombre del Archivo')
    
    auto_apply = fields.Boolean(
        string='Aplicar Automáticamente',
        default=False,
        help="Si está marcado, el diseño se aplicará automáticamente después del análisis"
    )
    
    backup_current = fields.Boolean(
        string='Hacer Backup del Diseño Actual',
        default=True,
        help="Recomendado: hace una copia de seguridad del diseño actual"
    )

    def action_generate_design(self):
        """Crea un nuevo generador de diseño y lo procesa"""
        self.ensure_one()
        
        # Crear el registro del generador
        generator = self.env['poliza.design.generator'].create({
            'name': self.name,
            'design_type': self.design_type,
            'pdf_file': self.pdf_file,
            'pdf_filename': self.pdf_filename,
        })
        
        # Analizar el PDF
        try:
            generator.action_analyze_pdf()
            
            # Si está configurado para aplicar automáticamente
            if self.auto_apply and generator.state == 'ready':
                generator.action_apply_design()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '¡Diseño Aplicado!',
                        'message': f'El diseño "{self.name}" ha sido generado y aplicado exitosamente.',
                        'type': 'success',
                        'sticky': True,
                    }
                }
            else:
                # Mostrar el formulario del generador para revisión
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Revisar Diseño Generado',
                    'res_model': 'poliza.design.generator',
                    'res_id': generator.id,
                    'view_mode': 'form',
                    'target': 'current',
                }
                
        except Exception as e:
            raise UserError(f"Error al generar el diseño: {str(e)}")

    def action_cancel(self):
        """Cancela el asistente"""
        return {'type': 'ir.actions.act_window_close'}