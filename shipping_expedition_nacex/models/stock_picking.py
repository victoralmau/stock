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

from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.one
    def generate_shipping_expedition(self):
        #operations
        if self.carrier_id.carrier_type=='nacex':
            self.generate_shipping_expedition_nacex()
        #return
        return super(StockPicking, self).generate_shipping_expedition()
        
    @api.one
    def generate_shipping_expedition_nacex(self):
        if self.shipping_expedition_id.id==0 and self.carrier_id.carrier_type=='nacex' and self.partner_id.id>0:
            res = self.nacex_ws_putExpedicion()[0]
            #operations
            if res['errors']==True:
                #logger
                _logger.info(res)
                #action_error_create_shipping_expedition_message_slack
                self.action_error_create_shipping_expedition_message_slack({
                    'error': res['error']
                })  
                #raise
                raise exceptions.Warning(res['error'])
            else:                             
                #create            
                shipping_expedition_vals = {
                    'picking_id': self.id,
                    'carrier_id': self.carrier_id.id,
                    'partner_id': self.partner_id.id,
                    'code': res['return']['result']['expe_codigo'],
                    'delivery_code': res['return']['result']['ag_cod_num_exp'],
                    'date': res['return']['result']['fecha_objetivo'],
                    'hour': res['return']['result']['hora_entrega'],
                    'origin': self.name,
                    'observations': res['return']['result']['cambios'],
                    'state': 'generate',
                    'state_code': 2,                
                }
                # url_info
                if '/' in shipping_expedition_vals['delivery_code']:
                    delivery_code_split = shipping_expedition_vals['delivery_code'].split("/")
                    if len(delivery_code_split) > 1:
                        shipping_expedition_vals['url_info'] = "http://www.nacex.es/seguimientoDetalle.do?agencia_origen=" + str(delivery_code_split[0]) + "&numero_albaran=" + str(delivery_code_split[1]) + "&estado=4&internacional=0&externo=N&usr=null&pas=null"
                # order_id
                if self.order_id.id > 0:
                    shipping_expedition_vals['order_id'] = self.order_id.id
                    # user_id
                    if self.order_id.user_id.id > 0:
                        shipping_expedition_vals['user_id'] = self.order_id.user_id.id
                # create
                if 'user_id' in shipping_expedition_vals:
                    shipping_expedition_obj = self.env['shipping.expedition'].sudo(
                        shipping_expedition_vals['user_id']).create(shipping_expedition_vals)
                else:
                    shipping_expedition_obj = self.env['shipping.expedition'].sudo().create(shipping_expedition_vals)
                #update
                self.shipping_expedition_id = shipping_expedition_obj.id
                #Fix
                self.action_view_etiqueta_item()
    
    @api.one
    def nacex_ws_putExpedicion(self):
        #define        
        today = datetime.today()
        datetime_body = today.strftime('%d/%m/%Y')
        #partner_name        
        if self.partner_id.name==False:
            partner_name = self.partner_id.parent_id.name 
        else:
            partner_name = self.partner_id.name
        # Fix solicitud mal formada
        partner_name = partner_name.replace('&', '')
        #street2
        obs1 = ''
        obs2 = ''
        if self.partner_id.street2!=False:
            street2_len = len(str(self.partner_id.street2))
            if(street2_len<=38):
                obs1 = self.partner_id.street2
            else:
                obs1 = self.partner_id.street2[0:38]
                obs2 = self.partner_id.street2[37:75].replace('&', '')
        #notes
        obs3 = ''
        obs4 = ''        
        if self.shipping_expedition_note!=False:
            shipping_expedition_note_len = len(str(self.shipping_expedition_note))
            if(shipping_expedition_note_len>1):
                if(shipping_expedition_note_len<=38):
                    obs3 = self.shipping_expedition_note                                
                else:
                    obs3 = self.shipping_expedition_note[0:38]
                    obs4 = self.shipping_expedition_note[37:75]
        #phone        
        partner_picking_phone = ''        
        if self.partner_id.mobile!=False:
            partner_picking_phone = self.partner_id.mobile
        elif self.partner_id.phone!=False:
            partner_picking_phone = self.partner_id.phone
        #tools
        nacex_username = tools.config.get('nacex_username')
        nacex_password = tools.config.get('nacex_password')
        #tip_ser
        tip_ser = str(self.carrier_id.nacex_tip_ser)
        if self.partner_id.country_id.code not in ['ES', 'PT', 'AD']:
            tip_ser = str(self.carrier_id.nacex_tip_ser_int)
        #tip_ser (Baleares) 20 - NACEX MALLORCA MARÍTIMO
        if self.partner_id.country_id.code == 'ES' and self.partner_id.state_id.code == 'PM':
            tip_ser = '20'
        #tip_env
        tip_env = str(self.carrier_id.nacex_tip_env)
        if self.partner_id.country_id.code not in ['ES', 'PT', 'AD']:
            tip_env = str(self.carrier_id.nacex_tip_env_int)
        #create
        url="http://gprs.nacex.com/nacex_ws/soap"
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:typ="urn:soap/types">
        		<soapenv:Header/>
        		<soapenv:Body>
        			<typ:putExpedicion>
        				<String_1>"""+str(nacex_username)+"""</String_1>
        				<String_2>"""+str(nacex_password)+"""</String_2>
        				<arrayOfString_3>del_cli="""+str(self.carrier_id.nacex_del_cli)+"""</arrayOfString_3>
        				<arrayOfString_3>num_cli="""+str(self.carrier_id.nacex_num_cli)+"""</arrayOfString_3>
        				<arrayOfString_3>fec="""+str(datetime_body)+"""</arrayOfString_3>
        				<arrayOfString_3>dep_cli="""+str(self.carrier_id.nacex_dep_cli)+"""</arrayOfString_3>
        				<arrayOfString_3>tip_ser="""+str(tip_ser)+"""</arrayOfString_3>
        				<arrayOfString_3>tip_cob="""+str(self.carrier_id.nacex_tip_cob)+"""</arrayOfString_3>
        				<arrayOfString_3>tip_env="""+str(tip_env)+"""</arrayOfString_3>
        				<arrayOfString_3>obs1="""+str(obs1)+"""</arrayOfString_3>
                        <arrayOfString_3>obs2="""+str(obs2)+"""</arrayOfString_3>
                        <arrayOfString_3>obs3="""+str(obs3)+"""</arrayOfString_3>
                        <arrayOfString_3>obs4="""+str(obs4)+"""</arrayOfString_3>        				        				
        				<arrayOfString_3>ref_cli="""+str(self.name)+"""</arrayOfString_3>					
        				<arrayOfString_3>bul=1</arrayOfString_3>
        				<arrayOfString_3>kil="""+str(self.weight)+"""</arrayOfString_3>
                        <arrayOfString_3>nom_rec="""+str(self.company_id.website)+"""</arrayOfString_3>
                        <arrayOfString_3>dir_rec="""+str(self.company_id.street[0:60])+"""</arrayOfString_3>
                        <arrayOfString_3>cp_rec="""+str(self.company_id.zip)+"""</arrayOfString_3>
                        <arrayOfString_3>pob_rec="""+str(self.company_id.city[0:39])+"""</arrayOfString_3>
                        <arrayOfString_3>tel_rec="""+str(self.company_id.phone)+"""</arrayOfString_3>
        				<arrayOfString_3>nom_ent="""+str(partner_name[0:50])+"""</arrayOfString_3>
                        <arrayOfString_3>per_ent="""+str(partner_name[0:35])+"""</arrayOfString_3>
        				<arrayOfString_3>dir_ent="""+str(self.partner_id.street[0:60])+"""</arrayOfString_3>                    
        				<arrayOfString_3>pais_ent="""+str(self.partner_id.country_id.code)+"""</arrayOfString_3>					
        				<arrayOfString_3>cp_ent="""+str(self.partner_id.zip)+"""</arrayOfString_3>
        				<arrayOfString_3>pob_ent="""+str(self.partner_id.city[0:39])+"""</arrayOfString_3>
        				<arrayOfString_3>tel_ent="""+str(partner_picking_phone)+"""</arrayOfString_3>        				        				
        			"""
        #con
        if self.partner_id.country_id.code not in ['ES', 'PT', 'AD']:
            #con
            con = '' 
            for pack_operation_product_id in self.pack_operation_product_ids:
                if pack_operation_product_id.product_id.id>0:
                   con += str(pack_operation_product_id.product_id.name)+','
            #val_dec            
            val_dec = "0.0"
            if self.origin!=False:
                sale_order_ids = self.env['sale.order'].sudo().search([('name', '=', self.origin)])
                if len(sale_order_ids)>0:
                    sale_order_id = sale_order_ids[0]
                    val_dec = sale_order_id.amount_total
            #body
            body += """
                        <arrayOfString_3>con="""+str(con[0:80])+"""</arrayOfString_3>
        				<arrayOfString_3>val_dec="""+str(val_dec)+"""</arrayOfString_3>"""
        #prealerta
        if self.partner_id.mobile!= False:
            body += """
                        <arrayOfString_3>tip_pre1=S</arrayOfString_3>
        				<arrayOfString_3>mod_pre1=S</arrayOfString_3>
        				<arrayOfString_3>pre1="""+str(self.partner_id.mobile)+"""</arrayOfString_3>"""
        #final
        body += """
                    </typ:putExpedicion>
        		</soapenv:Body>
        	</soapenv:Envelope>"""
        b = StringIO.StringIO()
        #continue
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
                    'fecha_objetivo': datetime.strptime(response['return']['results'][10], "%d/%m/%Y").date(),                   
                    'cambios': response['return']['results'][11],
                    'origin': self.name 
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
            # Fix
            if len(response['return']['results']) > 0:
                if response['return']['results'][0] == "ERROR":
                    response['error'] = response['return']['results'][1]
            # log
            _logger.info(body)
        # return
        return response
    
    @api.one
    def view_etiqueta_nacex(self):
        #tools
        nacex_username = tools.config.get('nacex_username')
        nacex_password = tools.config.get('nacex_password')
        #define        
        delivery_code_split = self.shipping_expedition_id.delivery_code.split('/')
        #url
        url = "http://gprs.nacex.com/nacex_ws/ws?method=getEtiqueta&user="+str(nacex_username)+"&pass="+str(nacex_password)+"&data=ag="+str(delivery_code_split[0])+"%7Cnumero="+str(delivery_code_split[1])+"%7Cmodelo=IMAGEN_B"                
        
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
                'error': "No se puede generar la etiqueta de una expedicion que no esta creada todavia",
                'return_real': "",
            }
        #return
        return response;
    
    @api.one
    def action_view_etiqueta_item(self):
        if self.shipping_expedition_id.id>0:
            res = self.view_etiqueta_nacex()[0]
            if res['errors']==True:
                raise exceptions.Warning(res['error'])
            else:
                delivery_code_split = self.shipping_expedition_id.delivery_code.split('/')
                #vals
                ir_attachment_vals = {
                    'name': delivery_code_split[0]+"-"+delivery_code_split[1]+'.png',
                    'datas': base64.encodestring(res['return']),
                    'datas_fname': delivery_code_split[0]+"-"+delivery_code_split[1]+'.png',
                    'res_model': 'stock.picking',
                    'res_id': self.id
                }
                ir_attachment_obj = self.env['ir.attachment'].sudo().create(ir_attachment_vals)
                #update ir_attachment_id
                self.ir_attachment_id = ir_attachment_obj.id                 
                       
    @api.multi
    def action_view_etiqueta(self, package_ids=None):
        for obj in self:
            if obj.shipping_expedition_id.id>0:
                obj.action_view_etiqueta_item()                                                                              
    
    @api.multi
    def _get_expedition_image(self):
        #tools
        nacex_username = tools.config.get('nacex_username')
        nacex_password = tools.config.get('nacex_password')
        #operations
        self.ensure_one()
        if self.shipping_expedition_id.id>0:                
            if self.carrier_id.carrier_type == 'nacex':
                url_image_expedition = 'http://gprs.nacex.com/nacex_ws/ws?method=getEtiqueta&user='+str(nacex_username)+'&pass='+str(nacex_password)+'&data=codexp='+str(self.shipping_expedition_id.code)+'|modelo=IMAGEN'
                #return url_image_expedition
                file = cStringIO.StringIO(urllib.urlopen(url_image_expedition).read())
                img = Image.open(file)
                return img
                
    @api.one
    def _get_expedition_image_url_ir_attachment(self):
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