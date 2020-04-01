# -*- coding: utf-8 -*-
{
    'name': 'TSB Expedition WebService',
    'version': '1.3.3',
    'author': "@victor.almau",
    'license': 'AGPL-3',
    'category': 'Delivery',
    'complexity': 'normal',
    'depends': ['base_delivery_carrier_expedition'],
    'data': [        
        'data/ir_configparameter_data.xml',
        'views/shipping_expedition.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True    
 }
