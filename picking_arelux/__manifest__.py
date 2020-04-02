# -*- coding: utf-8 -*-
{
    'name': "Picking Arelux",
    'summary': """Picking Arelux""",    
    'author': "@victor.almau",
    'website': "http://www.arelux.com",
    'category': 'Test',
    'version': '1.5.9',
    'depends': ['base', 'delivery', 'sale', 'stock', 'account'],
    'data': [
        'data/ir_cron.xml',
        'views/delivery_carrier.xml',
        'views/sale_order.xml',
        'views/stock_quant.xml',
        'views/stock_inventory_line.xml',
        'views/stock_pack_operation_lot.xml',
        'views/stock_picking.xml',
        'views/stock_production_lot.xml',
        'views/stock_scrap.xml',         
    ],    
}