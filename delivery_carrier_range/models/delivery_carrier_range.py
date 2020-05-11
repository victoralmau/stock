# -*- coding: utf-8 -*-
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrierRange(models.Model):
    _name = 'delivery.carrier.range'
    _description = 'Delivery Carrier Range'
            
    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',        
        string='Transportista',
    )
    country_id = fields.Many2one(
        comodel_name='res.country',        
        string='Pais',
    )
    state_id = fields.Many2one(
        comodel_name='res.country.state',        
        string='Provincia',
    )        
    weight_range_start = fields.Float(
        string='Rango inicial'        
    )
    weight_range_end = fields.Float(
        string='Rango final'        
    )
    price = fields.Float(
        string='Precio'        
    )                            