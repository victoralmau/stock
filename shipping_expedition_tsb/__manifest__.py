# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Shipping Expedition TSB',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['shipping_expedition'],
    'data': [
        'views/delivery_carrier.xml',
        'views/shipping_expedition.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'auto_install': False,    
}