# -*- coding: utf-8 -*-
{
    'name': 'Shipping Expedition Send Sms Info',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['delivery', 'shipping_expedition', 'aws_sms_shipping_expedition'],
    'data': [
        'data/ir_cron.xml',
        'views/delivery_carrier.xml',
    ],
    'installable': True,
    'auto_install': False,    
}