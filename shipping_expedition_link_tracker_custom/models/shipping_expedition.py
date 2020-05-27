# -*- coding: utf-8 -*-
from openerp import _, api, exceptions, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    @api.multi
    def cron_shipping_expeditionsend_link_tracker_id_generate(self, cr=None, uid=False, context=None):
        # not nacex
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('link_tracker_id', '=', False),
                ('url_info', '!=', False)
            ], limit=1000
        )
        if len(shipping_expedition_ids) > 0:
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.action_generate_shipping_expedition_link_tracker()