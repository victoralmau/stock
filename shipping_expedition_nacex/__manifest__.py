# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Shipping Expedition Nacex',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['shipping_expedition', 'sale'],
    'external_dependencies': {
        'python' : ['suds', 'pycurl', 'boto'],
    },
    'data': [
        'views/delivery_carrier.xml',    
        'views/stock_picking.xml',
        'views/shipping_expedition.xml',        
        'report/shipping_expedition_views.xml',
        'report/report_nacex.xml',
    ],
    'installable': True,
    'auto_install': False,    
}