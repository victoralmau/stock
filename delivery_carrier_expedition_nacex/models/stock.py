# -*- coding: utf-8 -*-
# © 2013 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from operator import attrgetter

from openerp import _, api, exceptions, fields, models

from ..nacex.web_service import NacexWebService

import urllib, cStringIO

import logging
_logger = logging.getLogger(__name__)

import base64

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.multi
    def get_shipping_expedition_values(self, expedition):    
        self.ensure_one()                
        if self.carrier_id.carrier_type == 'nacex':
            return self._get_shipping_expedition_values(expedition)                           
        
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
    def action_view_etiqueta(self, package_ids=None):                
        self.ensure_one()
        user = self.env.user
        company = user.company_id        
        webservice_class = NacexWebService            

        if package_ids is None:
            packages = self._get_packages_from_picking()
            packages = sorted(packages, key=attrgetter('name'))
        else:
            # restrict on the provided packages
            package_obj = self.env['stock.quant.package']
            packages = package_obj.browse(package_ids)

        web_service = webservice_class(company)
        res = web_service.view_etiqueta(self, packages)
        
        if res['errors'] == False:                
            delivery_code_split = self.shipping_expedition_id.delivery_code.split('/')
                                         
            data = {}
            data['name'] = delivery_code_split[0]+"-"+delivery_code_split[1]+'.png'
            data['datas'] = base64.encodestring(res['return'])           
            data['datas_fname'] = delivery_code_split[0]+"-"+delivery_code_split[1]+'.png'
            data['res_model'] = 'stock.picking'
            data['res_id'] = self.id
            
            ir_attachment_obj = self.env['ir.attachment']        
            ir_id = ir_attachment_obj.create(data)
            
            return ir_id
        else:
            raise exceptions.Warning('\n'.join(res['return']))                                                                      
    
    @api.multi
    def _get_expedition_image(self):
        self.ensure_one()
        if self.shipping_expedition_id.id>0:                
            if self.carrier_id.carrier_type == 'nacex':
                user = self.env.user
                company = user.company_id
            
                url_image_expedition = 'http://gprs.nacex.com/nacex_ws/ws?method=getEtiqueta&user='+str(company.nacex_username)+'&pass='+str(company.nacex_password)+'&data=codexp='+str(self.shipping_expedition_id.code)+'|modelo=IMAGEN'
                #return url_image_expedition
                file = cStringIO.StringIO(urllib.urlopen(url_image_expedition).read())
                img = Image.open(file)
                return img
                
    @api.multi
    def _get_expedition_image_url_ir_attachment(self):
        self.ensure_one()
        if self.shipping_expedition_id.id>0:                
            if self.carrier_id.carrier_type == 'nacex':
                ir_attachment_ids = self.env['ir.attachment'].search(
                    [ 
                        ('res_model', '=', 'stock.picking'),
                        ('res_id', '=', self.id)
                     ]
                )
                return_url = ''
                for ir_attachment_id in ir_attachment_ids:
                    return_url = '/web/image/'+str(ir_attachment_id.id)
                    
                return return_url

    def decode_base64(self, data):
        """Decode base64, padding being optional.
    
        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.
    
        """
        missing_padding = len(data) % 4
        if missing_padding != 0:
            data += b'='* (4 - missing_padding)
        return base64.decodestring(data)

    @api.multi            
    def _generate_nacex_expedition(self, webservice_class=None, package_ids=None):    
        self.ensure_one()
        user = self.env.user
        company = user.company_id
        if webservice_class is None:
            webservice_class = NacexWebService

        if package_ids is None:
            packages = self._get_packages_from_picking()
            packages = sorted(packages, key=attrgetter('name'))
        else:
            # restrict on the provided packages
            package_obj = self.env['stock.quant.package']
            packages = package_obj.browse(package_ids)

        web_service = webservice_class(company)
        res = web_service.generate_expedition(self, packages)
        
        if res['errors'] == True:
            self.action_error_create_shipping_expedition_message_slack(res)#slack.message                    
            raise exceptions.Warning('\n'.join(res['error']))
        else:
            return {
                'code': res['return']['result']['expe_codigo'],
                'delivery_code': res['return']['result']['ag_cod_num_exp'],
                'date': res['return']['result']['fecha_objetivo'],
                'hour': res['return']['result']['hora_entrega'],
                'observations': res['return']['result']['cambios'],
                'state': 'generate',
                'state_code': 2,
                'exps_rels': '',
            }
                            
        return res['return']['result']        
    
    @api.multi
    def generate_shipping_expedition(self, package_ids=None):
        self.ensure_one()                        
        if self.carrier_id.carrier_type == 'nacex':
            return self._generate_nacex_expedition(package_ids=package_ids)
                    
        _super = super(StockPicking, self)
        return _super.generate_shipping_expedition(package_ids=package_ids)                           
                
    @api.multi            
    def _edit_nacex_expedition(self, webservice_class=None, package_ids=None):
        self.ensure_one()
        user = self.env.user
        company = user.company_id
        if webservice_class is None:
            webservice_class = NacexWebService

        if package_ids is None:
            packages = self._get_packages_from_picking()
            packages = sorted(packages, key=attrgetter('name'))
        else:
            # restrict on the provided packages
            package_obj = self.env['stock.quant.package']
            packages = package_obj.browse(package_ids)

        web_service = webservice_class(company)
        res = web_service.edit_expedition(self, packages)
        
        if res['errors'] == True:        
            self.action_error_edit_shipping_expedition_message_slack(res)#slack.message                                
            raise exceptions.Warning('\n'.join(res['error']))
                        
        return True               
    
    @api.multi
    def action_edit_shipping_expedition(self, package_ids=None):        
        self.ensure_one()                
        if self.carrier_id.carrier_type == 'nacex':
            return self._edit_nacex_expedition(package_ids=package_ids)
        _super = super(StockPicking, self)
        return _super.action_edit_shipping_expedition(package_ids=package_ids)
        
    @api.multi    
    def cron_change_auto_done_nacex(self, cr=None, uid=False, context=None):
        stock_picking_ids = self.env['stock.picking'].search(
            [
                ('picking_type_id', '=', 7),
                ('state', 'in', ('confirmed', 'partial_available', 'assigned')),
                ('carrier_type', '=', 'nacex'),
                ('shipping_expedition_id', '!=', False)
            ]
        )
        if stock_picking_ids!=False:                
            for stock_picking_id in stock_picking_ids:
                stock_picking_id.do_transfer()                                                                                    