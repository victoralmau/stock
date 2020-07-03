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

    @api.multi
    def action_confirm(self):
        return_data = super(SaleOrder, self).action_confirm()
        # operations
        for item in self:
            if item.state == 'sale':
                for picking_id in item.picking_ids:
                    picking_id.shipping_expedition_note = item.shipping_expedition_note
        # return
        return return_data