# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import base64
import logging

_logger = logging.getLogger(__name__)


class PolizaSeguro(models.Model):
    _name = 'poliza.seguro'
    _description = 'Póliza de Seguro Vehicular'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'numero_poliza desc'

    # Información básica de la póliza
    numero_poliza = fields.Char(
        string='Número de Póliza',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('poliza.seguro.sequence')
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('expired', 'Vencida'),
        ('cancelled', 'Cancelada')
    ], string='Estado', default='draft', tracking=True)

    # DATOS DEL TOMADOR DE SEGUROS
    tomador_id = fields.Many2one(
        'poliza.tomador',
        string='Tomador',
        required=True,
        tracking=True
    )
    tomador_cedula = fields.Char(
        related='tomador_id.cedula_rif',
        string='Cédula/RIF Tomador',
        readonly=True
    )
    
    # DATOS DEL ASEGURADO
    asegurado_id = fields.Many2one(
        'poliza.tomador',
        string='Asegurado',
        required=True,
        tracking=True,
        domain=[('es_asegurado', '=', True)]
    )
    asegurado_cedula = fields.Char(
        related='asegurado_id.cedula_rif',
        string='Cédula/RIF Asegurado',
        readonly=True
    )
    direccion = fields.Text(string='Dirección', required=True)
    telefono = fields.Char(string='Teléfono', required=True)

    # DATOS DE LA PÓLIZA
    vigencia_desde = fields.Datetime(
        string='Vigencia Desde',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    vigencia_hasta = fields.Datetime(
        string='Vigencia Hasta',
        required=True,
        tracking=True
    )
    hora_vigencia = fields.Char(string='Hora', default='12:00')
    
    tipo_pago = fields.Selection([
        ('contado', 'Contado'),
        ('credito', 'Crédito'),
        ('financiado', 'Financiado')
    ], string='Tipo de Pago', required=True)
    
    sucursal = fields.Char(string='Sucursal', required=True)
    canal_venta = fields.Selection([
        ('directo', 'Directo'),
        ('agente', 'Agente'),
        ('broker', 'Broker'),
        ('online', 'Online')
    ], string='Canal de Venta', required=True)
    
    frecuencia_pago = fields.Selection([
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual')
    ], string='Frecuencia de Pago', required=True)
    
    codigo_intermediarios = fields.Char(string='Código de Intermediarios')
    participacion = fields.Float(string='Participación (%)', digits=(5, 2))
    moneda = fields.Selection([
        ('VES', 'Bolívares'),
        ('USD', 'Dólares')
    ], string='Moneda', required=True, default='VES')

    # DATOS DEL RECIBO
    recibo_vigencia_desde = fields.Datetime(string='Recibo Vigencia Desde')
    recibo_vigencia_hasta = fields.Datetime(string='Recibo Vigencia Hasta')
    recibo_hora = fields.Char(string='Recibo Hora')
    tipo_movimiento = fields.Selection([
        ('emision', 'Emisión'),
        ('renovacion', 'Renovación'),
        ('endoso', 'Endoso'),
        ('anulacion', 'Anulación')
    ], string='Tipo de Movimiento', required=True, default='emision')
    
    recibo_sucursal = fields.Char(string='Recibo Sucursal')
    recibo_canal_venta = fields.Char(string='Recibo Canal de Venta')
    recibo_frecuencia_pago = fields.Char(string='Recibo Frecuencia de Pago')
    total_pagar = fields.Float(string='Total a Pagar', digits=(12, 2), required=True)

    # PLANES DE ASOCIADOS
    producto = fields.Selection([
        ('rcv', 'RCV (Responsabilidad Civil Vehicular)'),
        ('integral', 'Seguro Integral'),
        ('terceros', 'Seguro contra Terceros'),
        ('colision', 'Seguro de Colisión'),
        ('robo', 'Seguro contra Robo'),
        ('incendio', 'Seguro contra Incendio'),
        ('otros', 'Otros')
    ], string='Producto', required=True, default='rcv')

    # DATOS DEL VEHÍCULO
    vehiculo_id = fields.Many2one(
        'poliza.vehiculo',
        string='Vehículo',
        required=True,
        tracking=True
    )

    # COBERTURA
    datos_personal = fields.Text(string='Datos Personal')
    exceso_limite = fields.Float(string='Exceso Límite', digits=(12, 2))
    muerte_invalidez = fields.Float(string='Muerte e Invalidez', digits=(12, 2))
    danos_cosas = fields.Float(string='Daños a Cosas', digits=(12, 2))
    defensa_penal = fields.Float(string='Defensa Penal', digits=(12, 2))
    gastos_medicos = fields.Float(string='Gastos Médicos', digits=(12, 2))
    gastos_funerarios = fields.Float(string='Gastos Funerarios', digits=(12, 2))

    # Campos computados para el carnet RCV
    nombre_asegurador = fields.Char(
        related='asegurado_id.name',
        string='Nombre del Asegurador',
        readonly=True
    )
    cedula_rif_asegurador = fields.Char(
        related='asegurado_id.cedula_rif',
        string='Cédula/RIF Asegurador',
        readonly=True
    )
    telefono_asegurador = fields.Char(
        related='asegurado_id.telefono',
        string='Teléfono Asegurador',
        readonly=True
    )
    
    # Campos del vehículo para el carnet
    marca_vehiculo = fields.Char(
        related='vehiculo_id.marca',
        string='Marca',
        readonly=True
    )
    modelo_vehiculo = fields.Char(
        related='vehiculo_id.modelo',
        string='Modelo',
        readonly=True
    )
    puestos_vehiculo = fields.Integer(
        related='vehiculo_id.puestos',
        string='Puestos',
        readonly=True
    )
    placa_vehiculo = fields.Char(
        related='vehiculo_id.placa',
        string='Placa',
        readonly=True
    )
    color_vehiculo = fields.Char(
        related='vehiculo_id.color',
        string='Color',
        readonly=True
    )
    serial_carroceria = fields.Char(
        related='vehiculo_id.serial_carroceria',
        string='Serial Carrocería',
        readonly=True
    )
    
    # Campos adicionales para el nombre del tomador
    tomador_nombre = fields.Char(
        related='tomador_id.name',
        string='Nombre del Tomador',
        readonly=True
    )
    
    # Campo para el año del vehículo
    ano = fields.Integer(
        related='vehiculo_id.ano',
        string='Año del Vehículo',
        readonly=True
    )
    
    # Campo para el serial del motor
    serial_motor = fields.Char(
        related='vehiculo_id.serial_motor',
        string='Serial del Motor',
        readonly=True
    )
    
    # Campo para el tipo de vehículo
    tipo = fields.Selection(
        related='vehiculo_id.tipo',
        string='Tipo de Vehículo',
        readonly=True
    )
    
    # Campo para el uso del vehículo
    uso = fields.Selection(
        related='vehiculo_id.uso',
        string='Uso del Vehículo',
        readonly=True
    )
    
    # Campo para el combustible
    combustible = fields.Selection(
        related='vehiculo_id.combustible',
        string='Combustible',
        readonly=True
    )
    
    # Campo para la transmisión
    transmision = fields.Selection(
        related='vehiculo_id.transmision',
        string='Transmisión',
        readonly=True
    )
    
    # Campo para el valor comercial
    valor_comercial = fields.Float(
        related='vehiculo_id.valor_comercial',
        string='Valor Comercial',
        readonly=True
    )

    @api.onchange('vigencia_desde')
    def _onchange_vigencia_desde(self):
        """Calcula automáticamente la vigencia hasta (1 año después)"""
        if self.vigencia_desde:
            self.vigencia_hasta = self.vigencia_desde + timedelta(days=365)

    @api.onchange('tomador_id')
    def _onchange_tomador_id(self):
        """Copia datos del tomador a los campos de contacto"""
        if self.tomador_id:
            self.direccion = self.tomador_id.direccion
            self.telefono = self.tomador_id.telefono

    def action_activate(self):
        """Activa la póliza"""
        self.state = 'active'

    def action_cancel(self):
        """Cancela la póliza"""
        self.state = 'cancelled'

    def action_expire(self):
        """Marca la póliza como vencida"""
        self.state = 'expired'

    @api.model
    def check_expired_policies(self):
        """Método para ejecutar por cron y marcar pólizas vencidas"""
        expired_policies = self.search([
            ('state', '=', 'active'),
            ('vigencia_hasta', '<', fields.Datetime.now())
        ])
        expired_policies.write({'state': 'expired'})

    def name_get(self):
        """Personaliza el nombre mostrado en las relaciones"""
        result = []
        for record in self:
            name = f"{record.numero_poliza} - {record.asegurado_id.name}"
            result.append((record.id, name))
        return result

    def action_print_custom_pdf(self):
        """Genera PDF usando plantilla personalizada"""
        try:
            # Buscar plantilla por defecto
            template = self.env['pdf.template'].search([('is_default', '=', True)], limit=1)
            if not template:
                template = self.env['pdf.template'].search([], limit=1)
            
            if not template:
                raise models.UserError("No hay plantillas PDF configuradas. Por favor, configure una plantilla primero.")
            
            # Preparar datos para rellenar el PDF
            poliza_data = self._prepare_pdf_data()
            
            # Generar PDF
            pdf_content = template.fill_pdf_template(poliza_data)
            
            # Crear attachment
            filename = f"Poliza_{self.numero_poliza}.pdf"
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })
            
            # Retornar acción para descargar
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
            
        except Exception as e:
            _logger.error(f"Error al generar PDF personalizado: {str(e)}")
            raise models.UserError(f"Error al generar PDF: {str(e)}")

    def _prepare_pdf_data(self):
        """Prepara los datos de la póliza para rellenar el PDF"""
        # Formatear fechas
        vigencia_desde_str = self.vigencia_desde.strftime('%d/%m/%Y') if self.vigencia_desde else ''
        vigencia_hasta_str = self.vigencia_hasta.strftime('%d/%m/%Y') if self.vigencia_hasta else ''
        recibo_vigencia_desde_str = self.recibo_vigencia_desde.strftime('%d/%m/%Y') if self.recibo_vigencia_desde else ''
        recibo_vigencia_hasta_str = self.recibo_vigencia_hasta.strftime('%d/%m/%Y') if self.recibo_vigencia_hasta else ''
        
        return {
            # Datos básicos de la póliza
            'numero_poliza': self.numero_poliza or '',
            'vigencia_desde': vigencia_desde_str,
            'vigencia_hasta': vigencia_hasta_str,
            'hora_vigencia': self.hora_vigencia or '',
            'tipo_pago': dict(self._fields['tipo_pago'].selection).get(self.tipo_pago, '') if self.tipo_pago else '',
            'sucursal': self.sucursal or '',
            'canal_venta': dict(self._fields['canal_venta'].selection).get(self.canal_venta, '') if self.canal_venta else '',
            'frecuencia_pago': dict(self._fields['frecuencia_pago'].selection).get(self.frecuencia_pago, '') if self.frecuencia_pago else '',
            'codigo_intermediarios': self.codigo_intermediarios or '',
            'participacion': str(self.participacion) if self.participacion else '',
            'moneda': self.moneda or '',
            'total_pagar': str(self.total_pagar) if self.total_pagar else '',
            'producto': self.producto or '',
            
            # Datos del tomador
            'tomador_nombre': self.tomador_nombre or '',
            'tomador_cedula': self.tomador_cedula or '',
            'direccion': self.direccion or '',
            'telefono': self.telefono or '',
            
            # Datos del asegurado
            'nombre_asegurador': self.nombre_asegurador or '',
            'cedula_rif_asegurador': self.cedula_rif_asegurador or '',
            'telefono_asegurador': self.telefono_asegurador or '',
            
            # Datos del vehículo
            'marca_vehiculo': self.marca_vehiculo or '',
            'modelo_vehiculo': self.modelo_vehiculo or '',
            'puestos_vehiculo': str(self.puestos_vehiculo) if self.puestos_vehiculo else '',
            'placa_vehiculo': self.placa_vehiculo or '',
            'color_vehiculo': self.color_vehiculo or '',
            'serial_carroceria': self.serial_carroceria or '',
            'serial_motor': self.serial_motor or '',
            'ano': str(self.ano) if self.ano else '',
            'tipo': self.tipo or '',
            'uso': self.uso or '',
            'combustible': self.combustible or '',
            'transmision': self.transmision or '',
            'valor_comercial': str(self.valor_comercial) if self.valor_comercial else '',
            
            # Datos de cobertura
            'exceso_limite': str(self.exceso_limite) if self.exceso_limite else '',
            'muerte_invalidez': str(self.muerte_invalidez) if self.muerte_invalidez else '',
            'danos_cosas': str(self.danos_cosas) if self.danos_cosas else '',
            'defensa_penal': str(self.defensa_penal) if self.defensa_penal else '',
            'gastos_medicos': str(self.gastos_medicos) if self.gastos_medicos else '',
            'gastos_funerarios': str(self.gastos_funerarios) if self.gastos_funerarios else '',
            
            # Datos del recibo
            'recibo_vigencia_desde': recibo_vigencia_desde_str,
            'recibo_vigencia_hasta': recibo_vigencia_hasta_str,
            'recibo_hora': self.recibo_hora or '',
            'tipo_movimiento': dict(self._fields['tipo_movimiento'].selection).get(self.tipo_movimiento, '') if self.tipo_movimiento else '',
            'recibo_sucursal': self.recibo_sucursal or '',
            'recibo_canal_venta': self.recibo_canal_venta or '',
            'recibo_frecuencia_pago': self.recibo_frecuencia_pago or '',
        }
    
    def debug_pdf_data(self):
        """
        Método para debuggear los datos que se envían al PDF
        """
        poliza_data = self._prepare_pdf_data()
        
        message = f"DATOS DE LA PÓLIZA {self.numero_poliza}\n\n"
        message += f"Total de campos: {len(poliza_data)}\n\n"
        
        # Agrupar por categorías
        categories = {
            'Datos básicos': ['numero_poliza', 'vigencia_desde', 'vigencia_hasta', 'hora_vigencia', 'tipo_pago', 'sucursal', 'canal_venta', 'frecuencia_pago', 'codigo_intermediarios', 'participacion', 'moneda', 'total_pagar', 'producto'],
            'Tomador': ['tomador_nombre', 'tomador_cedula', 'direccion', 'telefono'],
            'Asegurado': ['nombre_asegurador', 'cedula_rif_asegurador', 'telefono_asegurador'],
            'Vehículo': ['marca_vehiculo', 'modelo_vehiculo', 'puestos_vehiculo', 'placa_vehiculo', 'color_vehiculo', 'serial_carroceria', 'serial_motor', 'ano', 'tipo', 'uso', 'combustible', 'transmision', 'valor_comercial'],
            'Cobertura': ['exceso_limite', 'muerte_invalidez', 'danos_cosas', 'defensa_penal', 'gastos_medicos', 'gastos_funerarios'],
            'Recibo': ['recibo_vigencia_desde', 'recibo_vigencia_hasta', 'recibo_hora', 'tipo_movimiento', 'recibo_sucursal', 'recibo_canal_venta', 'recibo_frecuencia_pago']
        }
        
        for category, fields in categories.items():
            message += f"📋 {category.upper()}:\n"
            for field in fields:
                if field in poliza_data:
                    value = poliza_data[field]
                    if value:
                        message += f"  ✅ {field}: '{value}'\n"
                    else:
                        message += f"  ⚪ {field}: (vacío)\n"
                else:
                    message += f"  ❌ {field}: (no encontrado)\n"
            message += "\n"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': f'Datos de Póliza {self.numero_poliza}',
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }