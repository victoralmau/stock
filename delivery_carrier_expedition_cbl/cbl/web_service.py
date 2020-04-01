# -*- coding: utf-8 -*-
import pycurl
import StringIO
import xml.etree.ElementTree as ET
import datetime

import logging
_logger = logging.getLogger(__name__)

from openerp import _, api, exceptions, fields, models, tools

import os
import codecs
import urllib
import urllib2
from xml.dom.minidom import parseString

import requests
import unidecode
from bs4 import BeautifulSoup

import boto
from boto.s3.key import Key

class CblWebService():

    def __init__(self, company, env):
        self.company = company
        self.custom_env = env
        #confif
        self.sender_customer = self.custom_env['ir.config_parameter'].sudo().get_param('cbl_sender_customer')        
        self.s3_bucket = self.custom_env['ir.config_parameter'].sudo().get_param('cbl_s3_bucket')
        self.s3_folder = self.custom_env['ir.config_parameter'].sudo().get_param('cbl_s3_folder')
    
    def generate_expedition(self, picking, packages):
        delivery_carrier = picking.carrier_id       
        partner_picking = picking.partner_id
        country_partner_picking = partner_picking.country_id
        
        today = datetime.date.today()
        datetime_body = today.strftime('%d/%m/%Y')
        separator_fields = '#'        
        
        #partner_name
        if partner_picking.name==False:
            partner_name = partner_picking.parent_id.name 
        else:
            partner_name = partner_picking.name
    
        #partner_phone
        partner_phone = ''
        if partner_picking.mobile!=False:
            partner_phone = partner_picking.mobile
        else:
            if partner_picking.phone!=False:
                partner_phone = partner_picking.phone
    
        #partner_email
        if partner_picking.email==False:
            partner_email = ''
        else:
            partner_email = partner_picking.email
        
        #shipping_expedition_note
        if picking.shipping_expedition_note==False:
            observations1 = ''
            observations2 = ''
        else:
            observations1 = picking.shipping_expedition_note
            observations2 = ''
    
        txt_fields = [
            {
                'type': 'customer_reference',
                'value': str(picking.name),
                'size': 24,
            },
            {
                'type': 'sender_customer',
                'value': self.sender_customer,
                'size': 11,
            },            
            {
                'type': 'sender_name',
                'value': str(self.company.name),
                'size': 40,
            },
            {
                'type': 'sender_address',
                'value': str(self.company.street),
                'size': 40,
            },
            {
                'type': 'sender_country',
                'value': str(self.company.country_id.code),
                'size': 5,
            },
            {
                'type': 'sender_zip',
                'value': str(self.company.zip),
                'size': 7,
            },
            {
                'type': 'sender_city',
                'value': str(self.company.city),
                'size': 40,
            },
            {
                'type': 'sender_cif',
                'value': str(self.company.vat),
                'size': 16,
            },
            {
                'type': 'receiver_name',
                'value': str(partner_name[0:40]),
                'size': 40,
            },
            {
                'type': 'receiver_address',
                'value': str(partner_picking.street),
                'size': 40,
            },
            {
                'type': 'receiver_country',
                'value': str(partner_picking.country_id.code),
                'size': 5,
            },
            {
                'type': 'receiver_zip',
                'value': str(partner_picking.zip),
                'size': 7,
            },
            {
                'type': 'receiver_city',
                'value': str(partner_picking.city),
                'size': 40,
            },
            {
                'type': 'receiver_cif',
                'value': str(partner_picking.vat),
                'size': 16,
            },
            {
                'type': 'receiver_person',
                'value': str(partner_name),
                'size': 40,
            },
            {
                'type': 'receiver_phone',
                'value': str(partner_phone),
                'size': 15,
            },
            {
                'type': 'packs',
                'value': str(picking.number_of_packages),
                'size': 4,
            },
            {
                'type': 'kgs',
                'value': str(int(picking.weight)),
                'size': 5,
            },
            {
                'type': 'volume',
                'value': '000.000',
                'size': 7.3,
            },
            {
                'type': 'shipping_type',
                'value': 'P',
                'size': 4,
            },
            {
                'type': 'observations1',
                'value': str(observations1),
                'size': 100,
            },
            {
                'type': 'observations2',
                'value': str(observations2),
                'size': 100,
            },                                    
            {
                'type': 'return_conform',
                'value': 'N',
                'size': 1,
            },
            {
                'type': 'identicket',
                'value': 'N',
                'size': 1,
            },                                    
            {
                'type': 'refund_amount',
                'value': str(format(picking.total_cashondelivery, '.2f')),
                'size': 10.2,
            },            
            {
                'type': 'type_commission_reimbursement_commission',
                'value': 'P',
                'size': 1,
            },
            {
                'type': 'declared_value_amount',
                'value': '0000000.00',
                'size': 10.2,
            },
            {
                'type': 'tk_mailidio',
                'value': str(partner_picking.country_id.code),
                'size': 5,
            },
            {
                'type': 'tk_mail',
                'value': '',
                'value': str(partner_email),
                'size': 250,
            },
            {
                'type': 'liberated_expedition',
                'value': 'S',
                'size': 1,
            },                                                                                                            
        ]
        
        txt_line = ''
        for txt_field in txt_fields:                    
            txt_line = txt_line + str(txt_field['value'])+separator_fields
                
        txt_line = txt_line[:-1]#fix remove last character
        txt_line = txt_line + '\r\n'#fix new line
        #error prev
        response = {
            'errors': True, 
            'error': "", 
            'return': "",
        }                                                
        #open file for reading
        picking_name_replace = picking.name.replace("/", "-")
        file_name_real = str(picking_name_replace)+'.txt'
        file_name = os.path.dirname(os.path.abspath(__file__))+'/'+file_name_real                    
        #check if exists line
        line_exist_in_file = False
        if os.path.isfile(file_name):
            line_exist_in_file=True                        
        #continue line_exist_in_file
        if line_exist_in_file==False:            
            #fh = open(file_name,'a')# if file does not exist, create it
            fh = codecs.open(file_name, "a", "utf-8-sig")                            
            fh.write(txt_line)
            fh.close()
            #upload_s3
            destination_filename = str(self.s3_folder)+str(file_name_real)            
            return_upload_to_s3 = self.custom_env['s3.model'].sudo().upload_to_s3(file_name, destination_filename, self.s3_bucket, True)
            if return_upload_to_s3==False:
                response = {
                    'errors': True, 
                    'error': "Error al copiar el archivo en S3", 
                    'return': "",
                }
                return response                                   
            #change return and generate shipping_expedition
            response['errors'] = False                      
        else:
            response = {
                'errors': True, 
                'error': "Ya existe este albaran en el archivo .txt", 
                'return': "",
            }
            
        return response  
    
    def status_expedition(self, shipping_expedition):
        url = 'https://clientes.cbl-logistica.com/public/consultaenvios.aspx'
        values = {}
        
        response = {
            'errors': True, 
            'error': "Pendiente de realizar", 
            'return': "",
        }
        
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')        
        inputs = soup.find_all('input')
        for input_field in inputs:
            if input_field['type']=='hidden':
                values[input_field['id']] = input_field['value']
            else:
                values[input_field['id']] = ''
        
        if 'WebCUI_usuario' in values:
            values['WebCUI_usuario'] = '500506010'
            response['errors'] = False
            response['error'] = ''
            response['return'] = {}
        
        if shipping_expedition.code!=False and shipping_expedition.code!="":
            if 'WebCUI_nenvio' in values:            
                values['WebCUI_nenvio'] = shipping_expedition.code
        else:
            if 'WebCUI_ref' in values:            
                values['WebCUI_ref'] = shipping_expedition.picking_id.name                                        
                    
        if response['errors']==False:                
            data = urllib.urlencode(values)
            response_data = urllib2.urlopen(url, data)        
            page = response_data.read()        
            soup = BeautifulSoup(page, 'html.parser')        
            trs = soup.find_all('tr')
            td0_previous = False            
            for tr in trs:            
                tds = tr.find_all('td')
                                                
                if len(tds)==1:
                    td0 = unidecode.unidecode(tds[0].text.lower())
                    if td0_previous=='observaciones':
                        response['return'][str(td0_previous)] = str(td0)
                        
                    td0_previous = td0
                    
                elif len(tds)==2:
                    td0 = unidecode.unidecode(tds[0].text.lower())
                    td0 = td0.replace(".", "").replace(":", "").replace(" ", "_")
                    td0_previous = td0
                                                            
                    td1 = tds[1].text
                                        
                    if td0=="situacion":
                        td1 = unidecode.unidecode(td1.lower())
                        td1 = td1.replace(" ", "_")
                                                                        
                    response['return'][str(td0)] = str(td1)                                     
        
        if 'situacion' not in response['return']:
            response['errors'] = True
                                                        
        return response                                                              