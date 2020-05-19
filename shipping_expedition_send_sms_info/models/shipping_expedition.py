# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'
    
    date_send_sms_info = fields.Datetime(
        string='Fecha sms info' 
    )
    
    @api.one
    def action_send_sms_info_real(self):
        sms_compose_message_vals = {
            'model': 'shipping.expedition',
            'res_id': self.id,
            'country_id': self.partner_id.mobile_code_res_country_id.id,
            'mobile': self.partner_id.mobile,
            'sms_template_id': self.carrier_id.sms_info_sms_template_id
        }
        #Fix user_id
        if self.user_id.id>0:
            self.env.user.id = self.user_id.id
            sms_compose_message_obj = self.env['sms.compose.message'].sudo(self.env.user.id).create(sms_compose_message_vals)
        else:
            sms_compose_message_obj = self.env['sms.compose.message'].sudo().create(sms_compose_message_vals)
            
        return_onchange_sms_template_id = sms_compose_message_obj.onchange_sms_template_id(self.carrier_id.sms_info_sms_template_id.id, 'shipping.expedition', self.id)
        
        sms_compose_message_obj.update({
            'sender': return_onchange_sms_template_id['value']['sender'],
            'message': return_onchange_sms_template_id['value']['message']                                                     
        })
        sms_compose_message_obj.send_sms_action()
        
        if sms_compose_message_obj.action_send==True:
            #save_log
            automation_log_vals = {                    
                'model': 'shipping.expedition',
                'res_id': self.id,
                'category': 'shipping_expedition',
                'action': 'send_sms',                                                                                                                                                                                           
            }
            automation_log_obj = self.env['automation.log'].sudo().create(automation_log_vals)
            #other                                                                                                                                                         
            self.date_send_sms_info = datetime.today()
            self.action_custom_send_sms_info_slack()#Fix Slack
    
    @api.one
    def action_send_sms_info(self):
        allow_send = False
        # operations
        if self.date_send_sms_info == False:
            if self.carrier_id.send_sms_info == True:
                if self.carrier_id.sms_info_sms_template_id != False:
                    if self.state not in ['error', 'generate', 'canceled', 'delivered']:
                        if self.partner_id.mobile != False and self.partner_id.mobile_code_res_country_id != False:
                            if self.carrier_id.carrier_type == 'nacex':
                                allow_send = True
                            else:
                                if self.delegation_name != False and self.delegation_phone != False:
                                    allow_send = True
                        # allow_send
                        if allow_send == True:
                            self.action_send_sms_info_real()
    
    @api.one 
    def cron_shipping_expeditionsend_sms_info_item(self):
        #Fix link_tracker_id
        if self.link_tracker_id.id==0:
            res = self.action_generate_shipping_expedition_link_tracker()
        #action_send_sms_info                        
        self.action_send_sms_info()
    
    @api.model
    def cron_shipping_expeditionsend_sms_info(self):
        # not nacex
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '!=', 'nacex'),
                ('carrier_id.send_sms_info', '=', True),
                ('carrier_id.sms_info_sms_template_id', '!=', False),
                ('state', 'not in', ('error', 'generate', 'canceled', 'delivered')),
                ('date_send_sms_info', '=', False),
                ('delegation_name', '!=', False),
                ('delegation_phone', '!=', False),
                ('partner_id.mobile', '!=', False),
                ('partner_id.mobile_code_res_country_id', '!=', False),
            ]
        )
        if len(shipping_expedition_ids) > 0:
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.cron_shipping_expeditionsend_sms_info_item()
        # nacex
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '=', 'nacex'),
                ('carrier_id.send_sms_info', '=', True),
                ('carrier_id.sms_info_sms_template_id', '!=', False),
                ('state', 'not in', ('error', 'generate', 'canceled', 'delivered')),
                ('date_send_sms_info', '=', False),
                ('partner_id.mobile', '!=', False),
                ('partner_id.mobile_code_res_country_id', '!=', False),
            ]
        )
        if len(shipping_expedition_ids) > 0:
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.cron_shipping_expeditionsend_sms_info_item()