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
    def action_generate_shipping_expedition_link_tracker(self):
        if self.link_tracker_id.id==0 or self.link_tracker_id.id==False:
            if self.carrier_id.carrier_type in ['txt', 'nacex'] and self.txt_url!=False:
                link_tracker_vals = {
                    'title': self.code,    
                    'url': self.txt_url,                
                }
                link_tracker_obj = self.env['link.tracker'].sudo().create(link_tracker_vals)
                if link_tracker_obj!=False:
                    self.link_tracker_id = link_tracker_obj.id
        
        return True                                                                                        