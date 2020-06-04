# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models

from datetime import datetime
import datetime

import logging
_logger = logging.getLogger(__name__)

from bs4 import BeautifulSoup
import requests

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'
            
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
    def action_update_state(self):
        #operations
        if self.carrier_id.carrier_type=='txt':
            self.action_update_state_txt()
        #return
        return super(ShippingExpedition, self).action_update_state()
        
    @api.one
    def action_update_state_txt(self):
        res = self.action_update_state_txt_real()[0]
        #operations
        if res['errors']==True:
            _logger.info(res)  
            self.action_error_update_state_expedition(res)#Fix error
        else:
            #fecha_entrega
            if 'fecha_entrega' in res['return']:
                if '/' in res['return']['fecha_entrega']: 
                    fecha_split = res['return']['fecha_entrega'].split('/')
                    self.date = fecha_split[2]+'-'+fecha_split[1]+'-'+fecha_split[0]
            #num_albaran
            if 'num_albaran' in res['return']:                                 
                self.code = res['return']['num_albaran']
            #observaciones
            if 'observaciones' in res['return']:                 
                self.observations = res['return']['observaciones']
            #destino_expedicion1
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
            #state update                
            if state_new!=False and state_new!=state_old:
                self.state = state_new
    
    @api.one
    def action_update_state_txt_real(self):
        response = {
            'errors': True, 
            'error': "Pendiente de realizar", 
            'return': "",
        }            
        
        page = requests.get(self.url_info)
        soup = BeautifulSoup(page.content, 'html.parser')                        
        estado_expedicion_input = soup.find('input', {'id': 'TxtEstadoExpedicion'})
        if estado_expedicion_input!=None:
            response['errors'] = False
            response['return'] = {}            
            response['return']['estado_expedicion'] = estado_expedicion_input.get('value')#Fix
        
            inputs = soup.find_all('input')
            for input_field in inputs:                
                if input_field['id']=='TxtDestinoExpedicion1':
                    response['return']['destino_expedicion1'] = input_field['value']
                elif input_field['id']=="TxtNumalbaran":
                    response['return']['num_albaran'] = input_field['value']
                elif input_field['id']=="TxtEstadoExpedicion":
                    response['return']['estado_expedicion'] = input_field['value']
                elif input_field['id']=="TxtFechaSalida":
                    response['return']['fecha_salida'] = input_field['value']
                elif input_field['id']=="TxtFechaEntrega":
                    if response['return']['estado_expedicion']=="ENTREGADO":
                        response['return']['fecha_entrega'] = input_field['value']                    
                elif input_field['id']=="TxtObservaciones":
                    response['return']['observaciones'] = input_field['value']                        
        
            if 'num_albaran' not in response['return']:
                response['errors'] = True
        #return                                                                                                    
        return response                                                                    