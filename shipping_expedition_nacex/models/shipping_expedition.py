# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, tools
from odoo.exceptions import Warning

import urllib, pycurl
from io import StringIO
import xml.etree.ElementTree as ET

import logging
_logger = logging.getLogger(__name__)

import base64
import sys

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'
    
    @api.one
    def action_update_state(self):
        #operations
        if self.carrier_id.carrier_type=='nacex':
            self.action_update_state_nacex()
        #return
        return super(ShippingExpedition, self).action_update_state()
        
    @api.one
    def action_update_state_nacex(self):
        if self.delivery_code!=False:
            res = self.nacex_ws_getEstadoExpedicion()[0]
            #operations
            if res['errors']==True:
                _logger.info(res)
                self.action_error_update_state_expedition(res)#Fix error
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
    
    @api.one
    def nacex_ws_getEstadoExpedicion(self):
        
        #tools
        nacex_username = tools.config.get('nacex_username')
        nacex_password = tools.config.get('nacex_password')
        #define
        delivery_code_split = self.delivery_code.split('/')
        #url
        url = "http://gprs.nacex.com/nacex_ws/ws?method=getEstadoExpedicion&&user="+str(nacex_username)+"&pass="+str(nacex_password)+"&data=origen="+str(delivery_code_split[0])+"%7Calbaran="+str(delivery_code_split[1])                
        
        b = StringIO.StringIO()
                    
        curl = pycurl.Curl()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)    
        curl.setopt(pycurl.FORBID_REUSE, 1)
        curl.setopt(pycurl.FRESH_CONNECT, 1)                        
        curl.setopt(pycurl.URL, url)        
        curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)")
        curl.setopt(pycurl.HTTPHEADER, ["Content-Type: text/xml; charset=utf-8"])
        curl.perform()
        
        response = {
            'errors': True, 
            'error': "", 
            'return': "",
        }
        
        if curl.getinfo(pycurl.RESPONSE_CODE) == 200:        
            response['errors'] = False
            
            response_curl = b.getvalue()
            response_curl_split = response_curl.split('|')
            
            if response_curl_split[0]=="ERROR":
                response['errors'] = True                
            else:                
                response['return'] = {
                    'label': "",                    
                }
                response['return']['result'] = {
                    'expe_codigo': response_curl_split[0],
                    'fecha': response_curl_split[1],
                    'hora': response_curl_split[2],
                    'observaciones': response_curl_split[3],
                    'estado': response_curl_split[4],
                    'estado_code': response_curl_split[5],
                    'origen': response_curl_split[6],
                    'albaran': response_curl_split[7]
                }
        else:
            response['error'] = b.getvalue()
            _logger.info('Response KO')            
            _logger.info(pycurl.RESPONSE_CODE)        
        #return                                            
        return response