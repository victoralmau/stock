# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'    
    _order = 'position'
    
    position = fields.Integer(
        string='Posicion'
    )                                                     