# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


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
        tracking=True
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
    producto = fields.Char(string='Producto', required=True)

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