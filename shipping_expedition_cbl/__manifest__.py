# -*- coding: utf-8 -*-
{
    'name': 'Shipping Expedition Cbl',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['shipping_expedition'],
    'external_dependencies': {
        'python' : ['boto'],
    },
    'data': [
        'views/delivery.xml',
        'views/res_config.xml',
        'views/res_partner.xml',
        'views/shipping_expedition.xml',
        'views/stock.xml',                                
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,    
}