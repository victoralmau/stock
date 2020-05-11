# -*- coding: utf-8 -*-
{
    'name': 'Delivery Carrier Range',
    'version': '12.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base', 'stock', 'delivery'],
    'data': [
        'views/stock.xml',
        'views/product.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,    
}