# -*- coding: utf-8 -*-
{
    'name': 'Ont Base Picking',
    'version': '10.0.1.0.0',
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base', 'purchase', 'sale', 'stock'],
    'data': [
        'views/sale_order.xml',
        'views/stock_picking.xml'
    ],
    'installable': True,
    'auto_install': False,
}