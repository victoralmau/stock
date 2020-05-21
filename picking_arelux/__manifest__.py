# -*- coding: utf-8 -*-
{
    'name': 'Picking Arelux',
    'version': '12.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base', 'ont_base_picking', 'delivery', 'sale', 'stock', 'account', 'shipping_expedition'],
    'data': [
        'data/ir_cron.xml',
        'views/delivery_carrier.xml',
        'views/sale_order.xml',
        'views/stock_quant.xml',
        'views/stock_inventory_line.xml',
        'views/stock_move.xml',
        'views/stock_picking.xml',
        'views/stock_production_lot.xml',
        'views/stock_return_picking.xml',
        'views/stock_scrap.xml',         
    ],
    'installable': True,
    'auto_install': False,    
}