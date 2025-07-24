# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PolizaVehiculo(models.Model):
    _name = 'poliza.vehiculo'
    _description = 'Vehículo para Póliza de Seguro'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'placa'

    # Información básica del vehículo
    name = fields.Char(
        string='Nombre del Vehículo',
        compute='_compute_name',
        store=True
    )
    
    marca = fields.Char(
        string='Marca',
        required=True,
        tracking=True
    )
    
    modelo = fields.Char(
        string='Modelo',
        required=True,
        tracking=True
    )
    
    puestos = fields.Integer(
        string='Puestos',
        required=True,
        default=5
    )
    
    version = fields.Char(
        string='Versión'
    )
    
    ano = fields.Integer(
        string='Año',
        required=True,
        tracking=True
    )
    
    tipo = fields.Selection([
        ('sedan', 'Sedán'),
        ('hatchback', 'Hatchback'),
        ('suv', 'SUV'),
        ('pickup', 'Pick-up'),
        ('coupe', 'Coupé'),
        ('convertible', 'Convertible'),
        ('wagon', 'Station Wagon'),
        ('van', 'Van'),
        ('camion', 'Camión'),
        ('moto', 'Motocicleta'),
        ('otro', 'Otro')
    ], string='Tipo', required=True)
    
    placa = fields.Char(
        string='Placa',
        required=True,
        tracking=True
    )
    
    serial_motor = fields.Char(
        string='Serial de Motor',
        required=True
    )
    
    uso = fields.Selection([
        ('particular', 'Particular'),
        ('comercial', 'Comercial'),
        ('publico', 'Público'),
        ('oficial', 'Oficial')
    ], string='Uso', required=True, default='particular')
    
    color = fields.Char(
        string='Color',
        required=True
    )
    
    serial_carroceria = fields.Char(
        string='Serial de Carrocería',
        required=True
    )
    
    otros = fields.Text(
        string='Otros Datos'
    )
    
    # Información adicional
    propietario_id = fields.Many2one(
        'poliza.tomador',
        string='Propietario'
    )
    
    valor_comercial = fields.Float(
        string='Valor Comercial',
        digits=(12, 2)
    )
    
    combustible = fields.Selection([
        ('gasolina', 'Gasolina'),
        ('diesel', 'Diesel'),
        ('gas', 'Gas'),
        ('electrico', 'Eléctrico'),
        ('hibrido', 'Híbrido')
    ], string='Combustible')
    
    transmision = fields.Selection([
        ('manual', 'Manual'),
        ('automatica', 'Automática'),
        ('cvt', 'CVT')
    ], string='Transmisión')
    
    # Relaciones
    polizas_ids = fields.One2many(
        'poliza.seguro',
        'vehiculo_id',
        string='Pólizas'
    )
    
    # Campos computados
    total_polizas = fields.Integer(
        string='Total de Pólizas',
        compute='_compute_total_polizas'
    )
    
    poliza_activa = fields.Boolean(
        string='Tiene Póliza Activa',
        compute='_compute_poliza_activa'
    )
    
    active = fields.Boolean(default=True)

    @api.depends('marca', 'modelo', 'ano', 'placa')
    def _compute_name(self):
        """Genera el nombre del vehículo automáticamente"""
        for record in self:
            if record.marca and record.modelo and record.ano and record.placa:
                record.name = f"{record.marca} {record.modelo} {record.ano} - {record.placa}"
            else:
                record.name = "Vehículo sin datos completos"

    @api.depends('polizas_ids')
    def _compute_total_polizas(self):
        """Calcula el total de pólizas del vehículo"""
        for record in self:
            record.total_polizas = len(record.polizas_ids)

    @api.depends('polizas_ids.state')
    def _compute_poliza_activa(self):
        """Verifica si el vehículo tiene una póliza activa"""
        for record in self:
            record.poliza_activa = any(
                poliza.state == 'active' for poliza in record.polizas_ids
            )

    @api.constrains('placa')
    def _check_placa_unique(self):
        """Valida que la placa sea única"""
        for record in self:
            if record.placa:
                existing = self.search([
                    ('placa', '=', record.placa),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise models.ValidationError(
                        f"Ya existe un vehículo registrado con la placa: {record.placa}"
                    )

    @api.constrains('serial_motor')
    def _check_serial_motor_unique(self):
        """Valida que el serial del motor sea único"""
        for record in self:
            if record.serial_motor:
                existing = self.search([
                    ('serial_motor', '=', record.serial_motor),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise models.ValidationError(
                        f"Ya existe un vehículo registrado con el serial de motor: {record.serial_motor}"
                    )

    @api.constrains('serial_carroceria')
    def _check_serial_carroceria_unique(self):
        """Valida que el serial de carrocería sea único"""
        for record in self:
            if record.serial_carroceria:
                existing = self.search([
                    ('serial_carroceria', '=', record.serial_carroceria),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise models.ValidationError(
                        f"Ya existe un vehículo registrado con el serial de carrocería: {record.serial_carroceria}"
                    )

    @api.constrains('ano')
    def _check_ano_valid(self):
        """Valida que el año sea válido"""
        import datetime
        current_year = datetime.datetime.now().year
        for record in self:
            if record.ano:
                if record.ano < 1900 or record.ano > current_year + 1:
                    raise models.ValidationError(
                        f"El año del vehículo debe estar entre 1900 y {current_year + 1}"
                    )

    def name_get(self):
        """Personaliza el nombre mostrado"""
        result = []
        for record in self:
            if record.marca and record.modelo and record.placa:
                name = f"{record.marca} {record.modelo} - {record.placa}"
            else:
                name = record.name or f"Vehículo ID: {record.id}"
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Permite buscar por marca, modelo o placa"""
        args = args or []
        if name:
            records = self.search([
                '|', '|', '|',
                ('marca', operator, name),
                ('modelo', operator, name),
                ('placa', operator, name),
                ('name', operator, name)
            ] + args, limit=limit)
            return records.name_get()
        return super().name_search(name, args, operator, limit)