# -*- coding: utf-8 -*-
{
    'name': 'Stock Pickings Do New Transfer',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['stock'],    
    'data': [
        'data/ir_configparameter_data.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'auto_install': False,    
}