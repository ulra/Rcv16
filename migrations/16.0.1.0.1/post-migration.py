# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Migración para convertir el campo moneda de Selection a Many2one
    """
    # Actualizar registros con moneda VES
    cr.execute("""
        UPDATE poliza_seguro 
        SET moneda = (SELECT id FROM res_currency WHERE name = 'VES' LIMIT 1)
        WHERE moneda = 'VES' OR moneda IS NULL
    """)
    
    # Actualizar registros con moneda USD
    cr.execute("""
        UPDATE poliza_seguro 
        SET moneda = (SELECT id FROM res_currency WHERE name = 'USD' LIMIT 1)
        WHERE moneda = 'USD'
    """)
    
    # Si no existe VES, usar la moneda de la compañía por defecto
    cr.execute("""
        UPDATE poliza_seguro 
        SET moneda = (SELECT currency_id FROM res_company WHERE id = 1 LIMIT 1)
        WHERE moneda IS NULL
    """)