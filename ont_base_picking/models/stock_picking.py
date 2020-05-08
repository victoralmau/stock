# -*- coding: utf-8 -*-
from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    number_of_packages = fields.Integer(
        string='Bultos',
        default=1
    )
    number_of_pallets = fields.Integer(
        string='Palets',
        default=1
    )
    sale_order_note = fields.Char( 
        string='Nota pedido de venta',
    )
    shipping_expedition_note = fields.Char( 
        string='Nota pedido de venta expedicion',
    )    