# -*- coding: utf-8 -*-
{
    'name': 'Shipping Expedition TXT',
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
        'data/ir_configparameter_data.xml',
        'data/ir_cron.xml',
        'views/shipping_expedition.xml',
        'views/stock_picking.xml',
    ],
    'installable': True,
    'auto_install': False,    
}