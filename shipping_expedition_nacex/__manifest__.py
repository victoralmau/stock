# -*- coding: utf-8 -*-
{
    'name': 'Shipping Expedition Nacex',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['shipping_expedition'],
    'external_dependencies': {
        'python' : ['suds', 'pycurl', 'boto'],
    },
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
}