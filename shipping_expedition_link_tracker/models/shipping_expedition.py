# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from odoo import fields, models, api

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'

    link_tracker_id = fields.Many2one(
        comodel_name='link.tracker', 
        string='Link Tracker Id'
    )

    @api.one
    def cron_shipping_expeditionsend_sms_info_item(self):
        # Fix link_tracker_id
        if self.link_tracker_id.id == 0:
            self.action_generate_shipping_expedition_link_tracker()
        # action_send_sms_info
        self.action_send_sms_info()

    @api.multi
    def action_generate_shipping_expedition_link_tracker_multi(self):
        for item in self:
            if item.link_tracker_id.id == 0:
                item.action_generate_shipping_expedition_link_tracker()

    @api.one
    def action_generate_shipping_expedition_link_tracker(self):
        if self.link_tracker_id.id == 0:
            if self.carrier_id.carrier_type in ['txt', 'nacex']:
                allow_create = False
                # conditions
                if self.carrier_id.carrier_type == 'txt' and self.txt_url != False:
                    link_tracker_vals = {
                        'title': self.code,
                        'url': self.txt_url
                    }
                    allow_create = True
                elif self.carrier_id.carrier_type == 'nacex' and self.nacex_url != False:
                    link_tracker_vals = {
                        'title': self.code,
                        'url': self.nacex_url
                    }
                    allow_create = True
                # create
                if allow_create == True:
                    link_tracker_obj = self.env['link.tracker'].sudo().create(link_tracker_vals)
                    self.link_tracker_id = link_tracker_obj.id
        # return
        return True