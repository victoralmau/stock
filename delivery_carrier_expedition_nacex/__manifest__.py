# -*- coding: utf-8 -*-
{
    'name': 'Nacex Expedition WebService',
    'version': '1.7.0',
    'author': "@victor.almau",
    'license': 'AGPL-3',
    'category': 'Delivery',
    'complexity': 'normal',
    'depends': ['base_delivery_carrier_expedition'],
    'data': [
        'data/ir_cron.xml',
        'data/res_partner.xml',
        
        'views/stock.xml',
        'views/res_config.xml',
        'views/shipping_expedition.xml',
        
        'report/shipping_expedition_views.xml',
        'report/report_nacex.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'external_dependencies': {
        'python': ['suds', 'pycurl'],
    }
 }
