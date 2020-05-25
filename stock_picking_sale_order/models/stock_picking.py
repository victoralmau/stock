# -*- coding: utf-8 -*-
from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Pedido',
        copy=False
    )
    confirmation_date_order = fields.Datetime(
        string='Fecha confirmacion pedido',
        store=True
    )