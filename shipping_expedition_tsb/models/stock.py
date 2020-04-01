# -*- coding: utf-8 -*-
# © 2013 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from operator import attrgetter

from openerp import _, api, exceptions, fields, models

from ..tsb.web_service import TsbWebService

import logging
import urllib, cStringIO

_logger = logging.getLogger(__name__)

import base64
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.multi
    def get_shipping_expedition_values(self, expedition):    
        self.ensure_one()                
        if self.carrier_id.carrier_type == 'tsb':
            return self._get_shipping_expedition_values(expedition)
            
        _super = super(StockPicking, self)
        return _super.get_shipping_expedition_values(expedition)                           
        
    @api.multi
    def _get_shipping_expedition_values(self, expedition):
        self.ensure_one()
        return {
            'code': expedition['code'],
            'delivery_code': expedition['delivery_code'],
            'date': expedition['date'],
            'hour': expedition['hour'],
            'observations': expedition['observations'],
            'state': expedition['state'],
            'state_code': expedition['state_code'],
            #'origin': expedition['origin'],
            #'delivery_note': expedition['delivery_note'],
            'exps_rels': expedition['exps_rels'],
        }                                              

    @api.multi            
    def _generate_tsb_expedition(self, webservice_class=None, package_ids=None):        
        self.ensure_one()
        user = self.env.user
        company = user.company_id
        
        if webservice_class is None:
            webservice_class = TsbWebService

        if package_ids is None:
            packages = self._get_packages_from_picking()
            packages = sorted(packages, key=attrgetter('name'))
        else:
            # restrict on the provided packages
            package_obj = self.env['stock.quant.package']
            packages = package_obj.browse(package_ids)

        web_service = webservice_class(company)
        #params
        web_service.sender_customer = self.env['ir.config_parameter'].sudo().get_param('tsb_sender_customer')
        #fix sender_center 02 - rollos
        web_service.sender_center = self.env['ir.config_parameter'].sudo().get_param('tsb_sender_center')        
        
        for pack_operation_product_id in self.pack_operation_product_ids:
            if pack_operation_product_id.product_id.product_tmpl_id.tsb_sender_center!=False and pack_operation_product_id.product_id.product_tmpl_id.tsb_sender_center!="":         
                web_service.sender_center = pack_operation_product_id.product_id.product_tmpl_id.tsb_sender_center
        
        web_service.tsb_ftp_host = self.env['ir.config_parameter'].sudo().get_param('tsb_ftp_host')
        web_service.tsb_ftp_user = self.env['ir.config_parameter'].sudo().get_param('tsb_ftp_user')
        web_service.tsb_ftp_password = self.env['ir.config_parameter'].sudo().get_param('tsb_ftp_password')
        web_service.tsb_ftp_directory_upload = self.env['ir.config_parameter'].sudo().get_param('tsb_ftp_directory_upload')
        web_service.tsb_ftp_directory_download = self.env['ir.config_parameter'].sudo().get_param('tsb_ftp_directory_download')
        #generate_expedition
        res = web_service.generate_expedition(self, packages)
        
        if res['errors'] == True:
            self.action_error_create_shipping_expedition_message_slack(res)#slack.message                                
            raise exceptions.Warning('\n'.join(res['error']))
        else:
            return {
                'code': '',
                'delivery_code': 'Generado '+str(self.name),
                'date': datetime.today().strftime("%Y-%m-%d"),
                'hour': '',
                'observations': '',
                'state': 'generate',
                'state_code': 2,
                'exps_rels': '',
            }        
        
    @api.multi
    def generate_shipping_expedition(self, package_ids=None):
        self.ensure_one()         
        if self.carrier_id.carrier_type == 'tsb':
            return self._generate_tsb_expedition(package_ids=package_ids)
            
        _super = super(StockPicking, self)
        return _super.generate_shipping_expedition(package_ids=package_ids)                                                        