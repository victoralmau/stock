# -*- coding: utf-8 -*-
# © 2013 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, exceptions, fields, models

from ..txt.web_service import TxtWebService
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'        
    
    txt_url = fields.Char(
        compute='_get_txt_url',
        store=False,
        string='TXT Url'
    )
    
    @api.one
    def define_delegation_phone_txt(self):
        delegations_txt = {
            'A CORUÑA': {'phone': '981078907'},
            'ALBACETE': {'phone': '967213921','phone2': '967592544'},            
            'ALCAÑIZ': {'phone': '978830655'},
            'ALGECIRAS': {'phone': '956698730'},
            'ALICANTE': {'phone': '965105294'},
            'ALMERIA': {'phone': '950315564'},
            'ARNEDO': {'phone': '941382806'},
            'AVILA': {'phone': '920213400'},
            'BARCELONA': {'phone': '936593776'},
            'BILBAO': {'phone': '944570066'},
            'BOROX': {'phone': '925527001'},
            'BURGOS': {'phone': '947484866'},
            'CACERES': {'phone': '924349243'},
            'CADIZ': {'phone': '902106836'},
            'CALATAYUD': {'phone': '976881206'},
            'CASTELLON': {'phone': '964204142'},
            'CIUDAD REAL': {'phone': '926274985'},
            'CORDOBA': {'phone': '957326068'},
            'CUENCA': {'phone': '969220154'},
            'GERONA': {'phone': '972477891'},
            'GRANADA': {'phone': '958491878'},
            'GUADALAJARA': {'phone': '949044023'},
            'HUELVA': {'phone': '959500193'},
            'HUESCA': {'phone': '974218946'},
            'IBIZA': {'phone': '971199932'},
            'LA CAROLINA': {'phone': '953681500'},
            'LEON': {'phone': '987269264'},
            'LISBOA': {'phone': '351210992094'},
            'LLEIDA': {'phone': '973257308'},
            'LOGROÑO': {'phone': '941257900'},
            'LUGO': {'phone': '982209158'},
            'MADRID': {'phone': '916878400'},
            'MADRIDEJOS': {'phone': '925245467'},
            'MALAGA': {'phone': '952179950', 'phone2': '952179951'},
            'MANRESA': {'phone': '938732770'},
            'MELILLA': {'phone': '952231130'},
            'MENORCA': {'phone': '971360834'},
            'MERIDA': {'phone': '924046212'},
            'MOLINA': {'phone': '968389160'},
            'NAVALMORAL': {'phone': '927538701'},
            'ORENSE': {'phone': '988256845'},
            'OVIEDO': {'phone': '985267730'},
            'PALENCIA': {'phone': '979043002'},
            'PALMA DE MALLORCA': {'phone': '971605097'},
            'PAMPLONA': {'phone': '948314381'},
            'PENDES': {'phone': '935169181'},
            'PONFERRADA': {'phone': '987419305'},
            'PUERTO DE SANTA MARIA': {'phone': '956858502'},            
            'SAN SEBASTIAN': {'phone': '943377575'},
            'SALAMANCA': {'phone': '923250695'},
            'SANTANDER': {'phone': '942334422'},            
            'SANTIAGO DE COMPOSTELA': {'phone': '981572341'},
            'SANTA CRUZ DE TENERIFE': {'phone': '922622640'},
            'SEGOVIA': {'phone': '921447152'},
            'SEVILLA': {'phone': '954260674'},
            'SORIA': {'phone': '975211477'},
            'TARRAGONA': {'phone': '977196871', 'phone2': '977196872'},
            'TERUEL': {'phone': '978605064'},
            'TORRIJOS': {'phone': '925761156'},
            'VALENCIA': {'phone': '961667593'},
            'VALLADOLID': {'phone': '983313876'},
            'VIC': {'phone': '938893217'},            
            'VIGO': {'phone': '986488100'},                                                            
            'VITORIA': {'phone': '945292900'},
            'ZAMORA': {'phone': '980045035'},
            'ZARAGOZA': {'phone': '976144588'},                                                                                                                                                                                                                                                                                                                                                                                                                       
        }
        if self.delegation_name!=False and self.delegation_name!="":
            delegation_name_search = str(self.delegation_name)
            #stranger_things
            if 'TORRIJOS' in delegation_name_search: 
                delegation_name_search = 'TORRIJOS'
            elif 'CIUDAD REAL' in delegation_name_search: 
                delegation_name_search = 'CIUDAD REAL'
            elif 'LEON' in delegation_name_search: 
                delegation_name_search = 'LEON'
                            
            if delegation_name_search=='TENERIFE MARITIMO':
                delegation_name_search = 'SANTA CRUZ DE TENERIFE'                                                                          
                
            if delegation_name_search in delegations_txt:
                self.delegation_phone = delegations_txt[delegation_name_search]['phone']
            else:
                #slack.message
                web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')                
                attachments = [
                    {                    
                        "title": 'No se ha encontrado el telefono de TXT para la delegacion *'+str(delegation_name_search)+'*',                        
                        "color": "#ff0000",                                             
                        "fallback": "Ver expedicion "+str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=shipping.expedition",                                    
                        "actions": [
                            {
                                "type": "button",
                                "text": "Ver expedicion",
                                "url": str(web_base_url)+"/web?#id="+str(self.id)+"&view_type=form&model=shipping.expedition"
                            }
                        ]                    
                    }
                ]                
                slack_message_vals = {
                    'attachments': attachments,
                    'model': self._inherit,
                    'res_id': self.id,
                    'channel': self.env['ir.config_parameter'].sudo().get_param('slack_arelux_log_almacen_channel'),                                                         
                }                        
                slack_message_obj = self.env['slack.message'].sudo().create(slack_message_vals)                                                            
    
    @api.one        
    def _get_txt_url(self):
        self.ensure_one()
                
        if self.carrier_type=="txt":
            if self.date!=False:
                if '-' in self.date:
                    date_split = self.date.split("-")                                
                    self.txt_url = "http://tracking.txt.es/?EXPED=@33701@fx4iqq5kj101tks@R@"+self.origin+"@"+date_split[0]+"@"                                
    
    @api.one
    def update_state_txt(self, webservice_class=None, is_cron_exec=False):    
        user = self.env.user
        
        company = user.company_id
        if webservice_class is None:
            webservice_class = TxtWebService
        
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
                    self.date = fecha_split[2]+'-'+fecha_split[1]+'-'+fecha_split[0]
            
            if 'num_albaran' in res['return']:                                 
                self.code = res['return']['num_albaran']
            
            if 'observaciones' in res['return']:                 
                self.observations = res['return']['observaciones']
            
            if 'destino_expedicion1' in res['return']:                 
                self.delegation_name = res['return']['destino_expedicion1']                
                self.define_delegation_phone_txt()                                
            #state
            state_old = self.state
            state_new = False
            
            if res['return']['estado_expedicion']=="ENTREGADO":
                state_new = "delivered"
            elif res['return']['estado_expedicion']=="EN REPARTO" or res['return']['estado_expedicion']=="EN TRANSITO":
                state_new = "in_transit"
            elif res['return']['estado_expedicion']=="INCIDENCIA" or res['return']['estado_expedicion']=="EN INCIDENCIA":
                state_new = "incidence"
                
            if state_new!=False and state_new!=state_old:
                self.state = state_new
                
                if state_new=="incidence":
                    res_to_slack = res
                    res_to_slack['error'] = res_to_slack['return']['observaciones']
                    self.action_incidence_expedition_message_slack(res_to_slack)#slack_message                    
                        
        return res                                                                                                                                 

    @api.one
    def update_state(self):           
        if self.carrier_id!=False:
            if self.carrier_id.id!=False:
                if self.carrier_id.id>0:             
                    if self.carrier_id.carrier_type == 'txt':
                        return self.update_state_txt(None)
                        
        return super(ShippingExpedition, self).update_state()
        
    @api.multi    
    def cron_update_shipping_expedition_state_txt(self, cr=None, uid=False, context=None):
        current_date = datetime.today()
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '=', 'txt'),
                ('state', 'not in', ('canceled', 'delivered')),
                ('create_date', '<', current_date.strftime("%Y-%m-%d"))
            ]
        )
        if len(shipping_expedition_ids)>0:
            for shipping_expedition_id in shipping_expedition_ids:            
                shipping_expedition_id.update_state_txt(None, True)
                        
    @api.multi    
    def cron_send_mail_info_txt(self, cr=None, uid=False, context=None):
        txt_expedition_info_template_id = self.env['ir.config_parameter'].sudo().get_param('txt_expedition_info_template_id')
        
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('carrier_id.carrier_type', '=', 'txt'),
                ('state', 'not in', ('error', 'generate','canceled', 'delivered')),
                ('date_send_mail_info', '=', False)
            ]
        )
        if len(shipping_expedition_ids)>0:
            for shipping_expedition_id in shipping_expedition_ids:    
                shipping_expedition_id.action_send_mail_info(txt_expedition_info_template_id)                                                            