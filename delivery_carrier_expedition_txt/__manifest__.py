# -*- coding: utf-8 -*-
{
    'name': 'TXT Expedition WebService',
    'version': '1.5.1',
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
