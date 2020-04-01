# -*- coding: utf-8 -*-
# © 2013 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, exceptions, fields, models

from ..tsb.web_service import TsbWebService

import logging

_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'        
    
    tsb_identiticket = fields.Char(
        string='Tsb Identiticket'
    )
    tsb_localizator = fields.Char(
        string='Tsb Localizador'
    )
    tsb_url = fields.Char(
        string='Tsb Url'
    )                
    
    @api.one
    def update_state_tsb(self, webservice_class=None):    
        user = self.env.user
        
        company = user.company_id
        if webservice_class is None:
            webservice_class = TsbWebService
        
        web_service = webservice_class(company)
        
        web_service.sender_customer = self.env['ir.config_parameter'].sudo().get_param('tsb_sender_customer')        
        web_service.tsb_ftp_host = self.env['ir.config_parameter'].sudo().get_param('tsb_ftp_host')
        web_service.tsb_ftp_user = self.env['ir.config_parameter'].sudo().get_param('tsb_ftp_user')
        web_service.tsb_ftp_password = self.env['ir.config_parameter'].sudo().get_param('tsb_ftp_password')
        web_service.tsb_ftp_directory_download = self.env['ir.config_parameter'].sudo().get_param('tsb_ftp_directory_download')
        
        res = web_service.status_expedition(self)                                                                                         

    @api.one
    def update_state(self):
        if self.carrier_id!=False:
            if self.carrier_id.id!=False:        
                if self.carrier_id.id>0:             
                    if self.carrier_id.carrier_type == 'tsb':
                        return self.update_state_tsb()
                                            
        return super(ShippingExpedition, self).update_state()                            