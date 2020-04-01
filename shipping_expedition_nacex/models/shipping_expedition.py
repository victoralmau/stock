# -*- coding: utf-8 -*-
# © 2013 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, exceptions, fields, models

from ..nacex.web_service import NacexWebService

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'        

    nacex_url = fields.Char(
        compute='_get_nacex_url',
        store=False
    )
    
    @api.one        
    def _get_nacex_url(self):                
        if self.carrier_type=="nacex":        
            delivery_code_split = self.delivery_code.split("/")
            self.nacex_url = "http://www.nacex.es/seguimientoDetalle.do?agencia_origen="+delivery_code_split[0]+"&numero_albaran="+delivery_code_split[1]+"&estado=4&internacional=0&externo=N&usr=null&pas=null"        

    @api.one
    def cancel_state_nacex(self, webservice_class=None):            
        user = self.env.user
        
        company = user.company_id
        if webservice_class is None:
            webservice_class = NacexWebService
        
        web_service = webservice_class(company)
        res = webservice_class.cancell_expedition(self)
        if res['errors'] == True:
            if res['error']=='':
                res['error'] = 'Error sin especificar'
                
            self.action_error_cancell_expedition_message_slack(res)#slack.message                                                
            
            raise exceptions.Warning(res['error'])
        else:
            self.unlink
            
    @api.one
    def cancel_state(self):        
        stock_picking = self.picking_id
        if stock_picking.carrier_id!=False:    
            if stock_picking.carrier_id.id>0:            
                if stock_picking.carrier_id.carrier_type == 'nacex':
                    return self.cancel_state_nacex(None)                    
                        
        return super(ShippingExpedition, self).cancel_state()                                                

    @api.one
    def update_state_nacex(self, webservice_class=None, is_cron_exec=False):            
        user = self.env.user
        
        company = user.company_id
        if webservice_class is None:
            webservice_class = NacexWebService
        
        web_service = webservice_class(company)
        res = web_service.status_expedition(self)
                        
        if res['errors'] == True:
            if res['error']=='':
                res['error'] = 'Error sin especificar'
                
            self.action_error_update_state_expedition_message_slack(res)#slack.message                                                    
            
            if is_cron_exec==False:                
                raise exceptions.Warning(res['error'])
        else:
            #other_fields
            fecha_split = res['return']['result']['fecha'].split('/')
            self.date = fecha_split[2]+'-'+fecha_split[1]+'-'+fecha_split[0]
            self.hour = res['return']['result']['hora']
            self.observations = res['return']['result']['observaciones']
            self.state_code = res['return']['result']['estado_code']
            #state
            state_old = self.state
            state_new = False
                                                      
            if res['return']['result']['estado']=="ERROR" or res['return']['result']['estado_code']==18:
                state_new = "error"                         
            elif res['return']['result']['estado']=="INCIDENCIA" or res['return']['result']['estado_code']==9 or res['return']['result']['estado_code']==17 or res['return']['result']['estado_code']==13:
                state_new = "incidence"                
            elif res['return']['result']['estado_code']==1 or res['return']['result']['estado_code']==11 or res['return']['result']['estado_code']==12 or res['return']['result']['estado_code']==15:
                state_new = "shipped"                
            elif res['return']['result']['estado_code']==2 or res['return']['result']['estado_code']==3 or res['return']['result']['estado']=="REPARTO" or res['return']['result']['estado']=="TRANSITO":
                state_new = "in_transit"                
            elif res['return']['result']['estado']=="DELEGACION" or res['return']['result']['estado_code']==16:
                state_new = "in_delegation"                                                
            elif res['return']['result']['estado_code']==4 or res['return']['result']['estado']=="ENTREGADO" or res['return']['result']['estado']=="OK" or res['return']['result']['estado']=="SOL SIN OK":
                state_new = "delivered"                   
            elif res['return']['result']['estado']=="ANULADA":
                state_new = "canceled"
                    
            if state_new!=False and state_new!=state_old:
                self.state = state_new
                
                if state_new=="incidence":
                    res_to_slack = res
                    res_to_slack['error'] = res_to_slack['return']['result']['observaciones']
                    self.action_incidence_expedition_message_slack(res_to_slack)#slack_message                    
                    
        return res                                                                                                                                                   

    @api.one
    def update_state(self):           
        if self.carrier_id!=False:    
            if self.carrier_id.id>0:            
                if self.carrier_id.carrier_type == 'nacex':
                    return self.update_state_nacex(None)
                    
        return super(ShippingExpedition, self).update_state()
                    
    @api.multi    
    def cron_update_shipping_expedition_state_nacex(self, cr=None, uid=False, context=None):
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '=', 'nacex'),
                ('state', 'not in', ('canceled', 'delivered'))                
            ]
        )
        if len(shipping_expedition_ids)>0:
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.update_state_nacex(None, True)                                                                                   