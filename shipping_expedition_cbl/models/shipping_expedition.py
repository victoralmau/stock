# -*- coding: utf-8 -*-
# © 2013 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, exceptions, fields, models

from ..cbl.web_service import CblWebService
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'        
    
    cbl_url = fields.Char(
        string='CBL Url'
    )                
    
    @api.one
    def update_state_cbl(self, webservice_class=None, is_cron_exec=False):    
        user = self.env.user
        
        company = user.company_id
        if webservice_class is None:
            webservice_class = CblWebService
        
        web_service = webservice_class(company, self.env)                        
        
        res = web_service.status_expedition(self)
        
        if res['errors'] == True:
            if res['error']=='':
                res['error'] = 'Error sin especificar'
                
            self.action_error_update_state_expedition_message_slack(res)#slack.message                
                        
            if is_cron_exec==False:                
                raise exceptions.Warning(res['error'])
        else:
            if 'fecha_entrega' in res['return']:
                if '/' in res['return']['fecha_entrega']:
                    fecha_split = res['return']['fecha_entrega'].split('/')
                    self.date = fecha_split[2][0:4]+'-'+fecha_split[1]+'-'+fecha_split[0]
            
            if 'detalle_del_envio_' in res['return']:                                 
                self.code = res['return']['detalle_del_envio_']
                
            if 'ag_destino' in res['return']:
                self.delegation_name = res['return']['ag_destino']
                
            if 'telefono' in res['return']:
                self.delegation_phone = res['return']['telefono']
                
            if 'observaciones' in res['return']:
                self.observations = res['return']['observaciones']                                                                                                                    
            #state
            state_old = self.state
            state_new = False
                        
            if res['return']['situacion']=="entregada" or res['return']['situacion']=="entregada_con_incidencia":
                state_new = "delivered"
            elif res['return']['situacion']=="en_gestion":
                state_new = "shipped"
            elif res['return']['situacion']=="en_destino":
                state_new = "in_delegation"
            elif res['return']['situacion']=="en_reparto" or res['return']['situacion']=="en_transito":
                state_new = "in_transit"
            elif res['return']['situacion']=="devuelta":
                state_new = "canceled"
            elif res['return']['situacion']=="incidencia":
                state_new = "incidence"                
            
            if state_new!=False and state_new!=state_old:
                self.state = state_new
                
                if state_new=="incidence":
                    res_to_slack = res
                    res_to_slack['error'] = res_to_slack['return']['observaciones']                    
                    self.action_incidence_expedition_message_slack(res_to_slack)#slack_message                    
                else:
                    #self.action_send_mail_info(82) 
                    _logger.info('action_send_mail_info')                                       
        
        return res                                                                                                             

    @api.one
    def update_state(self):           
        if self.carrier_id!=False:
            if self.carrier_id.id!=False:        
                if self.carrier_id.id>0:             
                    if self.carrier_id.carrier_type == 'cbl':
                        return self.update_state_cbl(None)
                                            
        return super(ShippingExpedition, self).update_state()        
                        
    @api.multi    
    def cron_update_shipping_expedition_state_cbl(self, cr=None, uid=False, context=None):
        current_date = datetime.today()
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '=', 'cbl'),
                ('state', 'not in', ('canceled', 'delivered')),
                ('create_date', '<', current_date.strftime("%Y-%m-%d"))
            ]
        )
        if len(shipping_expedition_ids)>0:
            for shipping_expedition_id in shipping_expedition_ids:            
                shipping_expedition_id.update_state_cbl(None, True)                                                                                                                                                        