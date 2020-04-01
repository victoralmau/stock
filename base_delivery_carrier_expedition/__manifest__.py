# -*- coding: utf-8 -*-
{
    'name': 'Base module for carrier expeditions',
    'version': '1.6.2',
    'author': '@victor.almau',
    'category': 'Delivery',
    'complexity': 'normal',
    'depends': ['delivery', 'stock'],
    'data': [
        'views/delivery.xml',
        'views/res_config.xml',
        'views/res_partner.xml',
        'views/shipping_expedition.xml',
        'views/stock.xml',                                
        'security/ir.model.access.csv',
    ],
    'tests': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
 }
