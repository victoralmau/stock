# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    @api.one
    def action_send_sms_info(self):
        return super(ShippingExpedition, self).action_send_sms_info()
    
    @api.model
    def cron_shipping_expeditionsend_sms_info(self):
        # not nacex
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '!=', 'nacex'),
                ('carrier_id.send_sms_info', '=', True),
                ('carrier_id.sms_info_sms_template_id', '!=', False),
                ('state', 'not in', ('error', 'generate', 'canceled', 'delivered', 'incidence')),
                ('date_send_sms_info', '=', False),
                ('delegation_name', '!=', False),
                ('delegation_phone', '!=', False),
                ('partner_id.mobile', '!=', False),
                ('partner_id.mobile_code_res_country_id', '!=', False),
            ]
        )
        if len(shipping_expedition_ids) > 0:
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.action_send_sms_info()
        # nacex
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '=', 'nacex'),
                ('carrier_id.send_sms_info', '=', True),
                ('carrier_id.sms_info_sms_template_id', '!=', False),
                ('state', 'not in', ('error', 'generate', 'canceled', 'delivered', 'incidence')),
                ('date_send_sms_info', '=', False),
                ('partner_id.mobile', '!=', False),
                ('partner_id.mobile_code_res_country_id', '!=', False),
            ]
        )
        if len(shipping_expedition_ids) > 0:
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.action_send_sms_info()