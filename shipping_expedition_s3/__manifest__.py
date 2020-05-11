# -*- coding: utf-8 -*-
{
    'name': 'Shipping expedition S3',
    'version': '12.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['shipping_expedition', 'ir_attachment_s3'],
    'data': [
        'views/delivery_carrier.xml',
    ],
    'installable': True,
    'auto_install': False,    
}