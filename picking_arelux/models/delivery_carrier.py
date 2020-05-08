# -*- coding: utf-8 -*-
from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'    
    _order = 'position'
    
    position = fields.Integer(
        string='Posicion'
    )                                                     