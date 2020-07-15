# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_expedition_note = fields.Char(
        string='Nota expedicion',
    )
    shipping_expedition_count = fields.Integer(
        compute='_compute_shipping_expedition_count',
        string="Expediciones",
    )

    def _compute_shipping_expedition_count(self):
        for item in self:
            item.shipping_expedition_count = len(self.env['shipping.expedition'].search([('order_id', '=', item.id)]))