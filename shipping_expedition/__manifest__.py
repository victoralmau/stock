# -*- coding: utf-8 -*-
{
    'name': 'Shipping expedition',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['base', 'delivery', 'stock', 'sale', 'cashondelivery', 'stock_picking_sale_order'],
    'data': [
        'data/ir_cron.xml',
        'views/delivery_carrier.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/shipping_expedition.xml',
        'views/stock_picking.xml',                                
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,    
}