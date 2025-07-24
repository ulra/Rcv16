# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PolizaTomador(models.Model):
    _name = 'poliza.tomador'
    _description = 'Tomador/Asegurado de Póliza'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Nombre Completo',
        required=True,
        tracking=True
    )
    
    cedula_rif = fields.Char(
        string='Cédula de Identidad / RIF',
        required=True,
        tracking=True
    )
    
    tipo_documento = fields.Selection([
        ('cedula', 'Cédula de Identidad'),
        ('rif', 'RIF'),
        ('pasaporte', 'Pasaporte')
    ], string='Tipo de Documento', required=True, default='cedula')
    
    direccion = fields.Text(
        string='Dirección',
        required=True
    )
    
    telefono = fields.Char(
        string='Teléfono',
        required=True
    )
    
    email = fields.Char(
        string='Correo Electrónico'
    )
    
    fecha_nacimiento = fields.Date(
        string='Fecha de Nacimiento'
    )
    
    estado_civil = fields.Selection([
        ('soltero', 'Soltero(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viudo', 'Viudo(a)'),
        ('union_libre', 'Unión Libre')
    ], string='Estado Civil')
    
    profesion = fields.Char(string='Profesión')
    
    # Información adicional
    es_tomador = fields.Boolean(
        string='Es Tomador',
        default=True,
        help="Indica si esta persona puede ser tomador de pólizas"
    )
    
    es_asegurado = fields.Boolean(
        string='Es Asegurado',
        default=True,
        help="Indica si esta persona puede ser asegurado en pólizas"
    )
    
    # Relaciones
    polizas_como_tomador = fields.One2many(
        'poliza.seguro',
        'tomador_id',
        string='Pólizas como Tomador'
    )
    
    polizas_como_asegurado = fields.One2many(
        'poliza.seguro',
        'asegurado_id',
        string='Pólizas como Asegurado'
    )
    
    # Campos computados
    total_polizas_tomador = fields.Integer(
        string='Total Pólizas como Tomador',
        compute='_compute_total_polizas',
        store=True
    )
    
    total_polizas_asegurado = fields.Integer(
        string='Total Pólizas como Asegurado',
        compute='_compute_total_polizas',
        store=True
    )
    
    active = fields.Boolean(default=True)

    @api.depends('polizas_como_tomador', 'polizas_como_asegurado')
    def _compute_total_polizas(self):
        """Calcula el total de pólizas"""
        for record in self:
            record.total_polizas_tomador = len(record.polizas_como_tomador)
            record.total_polizas_asegurado = len(record.polizas_como_asegurado)

    @api.constrains('cedula_rif')
    def _check_cedula_rif_unique(self):
        """Valida que la cédula/RIF sea única"""
        for record in self:
            if record.cedula_rif:
                existing = self.search([
                    ('cedula_rif', '=', record.cedula_rif),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise models.ValidationError(
                        f"Ya existe una persona registrada con la cédula/RIF: {record.cedula_rif}"
                    )

    def name_get(self):
        """Personaliza el nombre mostrado"""
        result = []
        for record in self:
            name = f"{record.name} ({record.cedula_rif})"
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Permite buscar por nombre o cédula/RIF"""
        args = args or []
        if name:
            records = self.search([
                '|',
                ('name', operator, name),
                ('cedula_rif', operator, name)
            ] + args, limit=limit)
            return records.name_get()
        return super().name_search(name, args, operator, limit)