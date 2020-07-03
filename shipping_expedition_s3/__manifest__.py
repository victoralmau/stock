# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Shipping expedition S3',
    'version': '12.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['shipping_expedition'],
    'external_dependencies': {
        'python3' : ['boto3'],
    },
    'data': [
        'views/delivery_carrier.xml',
    ],
    'installable': True,
    'auto_install': False,    
}