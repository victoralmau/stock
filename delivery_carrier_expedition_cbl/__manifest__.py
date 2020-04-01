# -*- coding: utf-8 -*-
{
    'name': 'CBL Expedition WebService',
    'version': '1.4.5',
    'author': "@victor.almau",
    'license': 'AGPL-3',
    'category': 'Delivery',
    'complexity': 'normal',
    'depends': ['base_delivery_carrier_expedition'],
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
    'application': True    
 }
