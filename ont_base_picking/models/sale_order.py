# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    picking_note = fields.Char(
        string='Nota albaran',
    )
    shipping_expedition_note = fields.Char(
        string='Nota expedicion',
    )
    picking_priority = fields.Selection(
        [
            ('0', 'No urgente'),
            ('1', 'Normal'),
            ('2', 'Urgente'),
            ('3', 'Muy Urgente'),
        ],
        default='1',
        string='Prioridad albaran',
    )

    def _create_delivery_line(self, carrier, price_unit):
        if price_unit > 0:
            return super(SaleOrder, self)._create_delivery_line(carrier, price_unit)

    @api.multi
    def action_confirm(self):
        return_data = super(SaleOrder, self).action_confirm()
        # operations
        for item in self:
            if item.state == 'sale':
                for picking_id in item.picking_ids:
                    picking_id.order_id = item.id
                    picking_id.confirmation_date_order = item.confirmation_date
                    picking_id.sale_order_note = item.picking_note
                    picking_id.shipping_expedition_note = item.shipping_expedition_note
                    picking_id.priority = item.picking_priority
        # return
        return return_data