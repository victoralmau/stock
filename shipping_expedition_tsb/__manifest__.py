# -*- coding: utf-8 -*-
{
    'name': 'Shipping Expedition TSB',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['shipping_expedition'],
    'data': [
        'data/ir_configparameter_data.xml',
        'views/shipping_expedition.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'auto_install': False,    
}