# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Shipping Expedition Send Mail Info',
    'version': '12.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['delivery', 'shipping_expedition'],
    'data': [
        'data/ir_cron.xml',
        'views/delivery_carrier.xml',
        'views/shipping_expedition.xml',
    ],
    'installable': True,
    'auto_install': False,    
}