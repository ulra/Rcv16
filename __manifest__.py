# -*- coding: utf-8 -*-
{
    'name': 'La Venezolana de Seguros y Vida',
    'version': '16.0.2.13.0',
    'category': 'Insurance',
    'summary': 'Gestión de Pólizas de Seguros Vehiculares',
    'description': """
        Módulo para la gestión completa de pólizas de seguros vehiculares
        de La Venezolana de Seguros y Vida.
        
        Características:
        - Gestión de tomadores y asegurados
        - Registro completo de vehículos
        - Manejo de pólizas con todos los datos requeridos
        - Generación automática de carnets RCV
        - Reportes de pólizas personalizados
        - Control de vigencias y pagos
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'depends': ['base', 'mail', 'web'],
    'external_dependencies': {
        'python': ['PyPDF2', 'reportlab'],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/design_generator_security.xml',
        'data/sequence_data.xml',
        'data/config_data.xml',
        'data/paperformat_data.xml',
        'views/poliza_views.xml',
        'views/tomador_views.xml',
        'views/vehiculo_views.xml',
        'views/menu_views.xml',
        'views/pdf_template_views.xml',
        'reports/carnet_rcv_report.xml',
        'reports/poliza_report.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}