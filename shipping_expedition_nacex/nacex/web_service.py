# -*- coding: utf-8 -*-
import logging
import pycurl
import StringIO
import xml.etree.ElementTree as ET
import datetime

_logger = logging.getLogger(__name__)

from openerp import _, api, exceptions, fields, models, tools

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class NacexWebService():
    
    def __init__(self, company):
        self.company = company
        self.nacex_username = tools.config.get('nacex_username')
        self.nacex_password = tools.config.get('nacex_password')                
    
    def view_etiqueta(self, picking, packages):
        if picking.shipping_expedition_id.id>0:
            delivery_code_split = picking.shipping_expedition_id.delivery_code.split('/')
        
            url = "http://gprs.nacex.com/nacex_ws/ws?method=getEtiqueta&user="+str(self.nacex_username)+"&pass="+str(self.nacex_password)+"&data=ag="+str(delivery_code_split[0])+"%7Cnumero="+str(delivery_code_split[1])+"%7Cmodelo=IMAGEN_B"                
            
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
                'return': "",
                'return_real': "",
            }
            
            if curl.getinfo(pycurl.RESPONSE_CODE) == 200:                                
                response_curl = b.getvalue()
                
                response_curl_split = response_curl.split('|')
                
                if response_curl_split[0]!="ERROR":
                    response['return_real'] = response_curl
                                
                    edits = [('-', '+'), ('_', '/'), ('*', '=')] # etc.
                    for search, replace in edits:
                        response_curl = response_curl.replace(search, replace)
                    
                    response_curl = response_curl.decode('base64')
                    
                    response['errors'] = False
                    response['return'] = response_curl 
        else:
            response = {
                'errors': True,  
                'return': "No se puede generar la etiqueta de una expedicion que no esta creada todavia",
                'return_real': "",
            }
                                                                               
        return response;    
        
    def status_expedition(self, shipping_expedition):
        if shipping_expedition.delivery_code!=False:
            delivery_code_split = shipping_expedition.delivery_code.split('/')
        
            url = "http://gprs.nacex.com/nacex_ws/ws?method=getEstadoExpedicion&&user="+str(self.nacex_username)+"&pass="+str(self.nacex_password)+"&data=origen="+str(delivery_code_split[0])+"%7Calbaran="+str(delivery_code_split[1])                
            
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
                        'albaran': response_curl_split[7],
                        'exps_rels': "", 
                    }
            else:
                response['error'] = b.getvalue()
                _logger.info('Response KO')            
                _logger.info(pycurl.RESPONSE_CODE)
                
        else:
            response = {
                'errors': True, 
                'error': "No se puede actualizar el estado de una expedicion que no existe todavia", 
                'return': "",
            }                
                                                    
        return response                                                        
            
    def generate_expedition(self, picking, packages):
    
        delivery_carrier = picking.carrier_id       
        partner_picking = picking.partner_id
        country_partner_picking = partner_picking.country_id
        
        today = datetime.date.today()
        datetime_body = today.strftime('%d/%m/%Y')
        #partner_name        
        if partner_picking.name==False:
            partner_name = partner_picking.parent_id.name 
        else:
            partner_name = partner_picking.name        
        #street2
        obs1 = ''
        obs2 = ''
        if partner_picking.street2!=False:
            street2_len = len(str(partner_picking.street2))
            if(street2_len<=38):
                obs1 = partner_picking.street2
            else:
                obs1 = partner_picking.street2[0:38]
                obs2 = partner_picking.street2[37:75]
        #notes
        obs3 = ''
        obs4 = ''        
        if picking.shipping_expedition_note!=False:
            shipping_expedition_note_len = len(str(picking.shipping_expedition_note))
            if(shipping_expedition_note_len>1):
                if(shipping_expedition_note_len<=38):
                    obs3 = picking.shipping_expedition_note                                
                else:
                    obs3 = picking.shipping_expedition_note[0:38]
                    obs4 = picking.shipping_expedition_note[37:75]
        #phone        
        partner_picking_phone = ''        
        if partner_picking.mobile!=False:
            partner_picking_phone = partner_picking.mobile
        elif partner_picking.phone!=False:
            partner_picking_phone = partner_picking.phone
        #tip_ser
        tip_ser = self.company.nacex_tip_ser
        
        url="http://gprs.nacex.com/nacex_ws/soap"
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:typ="urn:soap/types">
        		<soapenv:Header/>
        		<soapenv:Body>
        			<typ:putExpedicion>
        				<String_1>"""+str(self.nacex_username)+"""</String_1>
        				<String_2>"""+str(self.nacex_password)+"""</String_2>
        				<arrayOfString_3>del_cli="""+str(self.company.nacex_del_cli)+"""</arrayOfString_3>
        				<arrayOfString_3>num_cli="""+str(self.company.nacex_num_cli)+"""</arrayOfString_3>
        				<arrayOfString_3>fec="""+str(datetime_body)+"""</arrayOfString_3>
        				<arrayOfString_3>dep_cli="""+str(self.company.nacex_dep_cli)+"""</arrayOfString_3>
        				<arrayOfString_3>tip_ser="""+str(tip_ser)+"""</arrayOfString_3>
        				<arrayOfString_3>tip_cob="""+str(self.company.nacex_tip_cob)+"""</arrayOfString_3>
        				<arrayOfString_3>tip_env="""+str(self.company.nacex_tip_env)+"""</arrayOfString_3>
        				<arrayOfString_3>obs1="""+str(obs1)+"""</arrayOfString_3>
                        <arrayOfString_3>obs2="""+str(obs2)+"""</arrayOfString_3>
                        <arrayOfString_3>obs3="""+str(obs3)+"""</arrayOfString_3>
                        <arrayOfString_3>obs4="""+str(obs4)+"""</arrayOfString_3>        				        				
        				<arrayOfString_3>ref_cli="""+str(picking.name)+"""</arrayOfString_3>					
        				<arrayOfString_3>bul=1</arrayOfString_3>
        				<arrayOfString_3>kil="""+str(picking.weight)+"""</arrayOfString_3>
                        <arrayOfString_3>nom_rec="""+str(self.company.website)+"""</arrayOfString_3>
                        <arrayOfString_3>dir_rec="""+str(self.company.street[0:60])+"""</arrayOfString_3>
                        <arrayOfString_3>cp_rec="""+str(self.company.zip)+"""</arrayOfString_3>
                        <arrayOfString_3>pob_rec="""+str(self.company.city[0:39])+"""</arrayOfString_3>
                        <arrayOfString_3>tel_rec="""+str(self.company.phone)+"""</arrayOfString_3>
        				<arrayOfString_3>nom_ent="""+str(partner_name[0:50])+"""</arrayOfString_3>
                        <arrayOfString_3>per_ent="""+str(partner_name[0:35])+"""</arrayOfString_3>
        				<arrayOfString_3>dir_ent="""+str(partner_picking.street[0:60])+"""</arrayOfString_3>                    
        				<arrayOfString_3>pais_ent="""+str(country_partner_picking.code)+"""</arrayOfString_3>					
        				<arrayOfString_3>cp_ent="""+str(partner_picking.zip)+"""</arrayOfString_3>
        				<arrayOfString_3>pob_ent="""+str(partner_picking.city[0:39])+"""</arrayOfString_3>
        				<arrayOfString_3>tel_ent="""+str(partner_picking_phone)+"""</arrayOfString_3>        				        				
        			"""
        #prealerta
        if partner_picking.mobile!= False:
            body += """
                        <arrayOfString_3>tip_pre1=S</arrayOfString_3>
        				<arrayOfString_3>mod_pre1=S</arrayOfString_3>
        				<arrayOfString_3>pre1="""+str(partner_picking.mobile)+"""</arrayOfString_3>"""
        #final
        body += """
                    </typ:putExpedicion>
        		</soapenv:Body>
        	</soapenv:Envelope>"""

        b = StringIO.StringIO()
        
        curl = pycurl.Curl()
        curl.setopt(pycurl.WRITEFUNCTION, b.write)    
        curl.setopt(pycurl.FORBID_REUSE, 1)
        curl.setopt(pycurl.FRESH_CONNECT, 1)                        
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.POSTFIELDS, body)        
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
            
            root = ET.fromstring(response_curl)
            
            response['return'] = {
                'label': "",                    
                'results': []
            }
                                    
            for item in root.findall('{http://schemas.xmlsoap.org/soap/envelope/}Body'):                
                for item2 in item.findall('{urn:soap/types}putExpedicionResponse'):                    
                    for result in item2.findall('result'):
                        response['return']['results'].append(result.text)
            
            if response['return']['results'][0]=="ERROR":
                response['errors'] = True
                response['error'] = response['return']['results'][1]
            else:                                                                            
                response['return']['result'] = {
                    'expe_codigo': response['return']['results'][0],
                    'ag_cod_num_exp': response['return']['results'][1],
                    'color': response['return']['results'][2],
                    'ent_ruta': response['return']['results'][3],
                    'ent_cod': response['return']['results'][4],
                    'ent_nom': response['return']['results'][5],
                    'ent_tlf': response['return']['results'][6],
                    'serv': response['return']['results'][7],
                    'hora_entrega': response['return']['results'][8],
                    'barcode': response['return']['results'][9], 
                    'fecha_objetivo': datetime.datetime.strptime(response['return']['results'][10], "%d/%m/%Y").date(),                   
                    'cambios': response['return']['results'][11],
                    'origin': picking.name 
                }                                                                                                                                                                                                                                                      
            
        else:
            response['error'] = b.getvalue()
            _logger.info('Response KO')            
            _logger.info(pycurl.RESPONSE_CODE)
            
            response_curl = b.getvalue()            
            root = ET.fromstring(response_curl)
            
            _logger.info(response_curl)
            
            response['errors'] = True
            
            response['return'] = {
                'label': "",                    
                'results': []
            }
                                    
            for item in root.findall('{http://schemas.xmlsoap.org/soap/envelope/}Body'):                
                for item2 in item.findall('{urn:soap/types}putExpedicionResponse'):                    
                    for result in item2.findall('result'):
                        response['return']['results'].append(result.text)
            
            if response['return']['results'][0]=="ERROR":                
                response['error'] = response['return']['results'][1]            
                                            
        return response                                                                                                       
