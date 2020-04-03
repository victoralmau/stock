# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    carrier_type = fields.Selection(
        selection=[
            ('none', 'Ninguno'),
            ('cbl', 'Cbl'),
            ('nacex', 'Nacex'),
            ('tsb', 'Tsb'),
            ('txt', 'Txt'),
        ],
        string='Type',
        default='none'
    )    