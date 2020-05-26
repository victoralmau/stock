# -*- coding: utf-8 -*-
{
    'name': 'Shipping Expedition Link Tracker',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base', 'shipping_expedition', 'shipping_expedition_nacex', 'shipping_expedition_txt', 'link_tracker'],
    'data': [
        'views/shipping_expedition.xml',
    ],
    'installable': True,
    'auto_install': False,    
}