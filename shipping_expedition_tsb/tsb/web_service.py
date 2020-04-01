# -*- coding: utf-8 -*-
import logging
import pycurl
import StringIO
import xml.etree.ElementTree as ET
import datetime

_logger = logging.getLogger(__name__)

from openerp import _, api, exceptions, fields, models

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import ftplib

class TsbWebService():

    def __init__(self, company):
        self.company = company
    
    def generate_expedition(self, picking, packages):
        delivery_carrier = picking.carrier_id       
        partner_picking = picking.partner_id
        country_partner_picking = partner_picking.country_id
        
        today = datetime.date.today()
        datetime_body = today.strftime('%d/%m/%Y')
        separator_fields = '#'        
        
        if partner_picking.name==False:
            partner_name = partner_picking.parent_id.name 
        else:
            partner_name = partner_picking.name
    
        
        if partner_picking.phone==False:
            partner_phone = ''
        else:
            partner_phone = partner_picking.phone
    
    
        if partner_picking.email==False:
            partner_email = ''
        else:
            partner_email = partner_picking.email
    
        if picking.shipping_expedition_note==False:
            observations = ''
        else:
            observations = picking.shipping_expedition_note
    
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
                'type': 'sender_center',
                'value': self.sender_center,
                'size': 4,
            },
            {
                'type': 'sender_name',
                'value': str(self.company.name),
                'size': 60,
            },
            {
                'type': 'sender_address',
                'value': str(self.company.street),
                'size': 60,
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
                'size': 60,
            },
            {
                'type': 'sender_cif',
                'value': str(self.company.vat),
                'size': 16,
            },
            {
                'type': 'receiver_name',
                'value': str(partner_name[0:60]),
                'size': 60,
            },
            {
                'type': 'receiver_address',
                'value': str(partner_picking.street),
                'size': 60,
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
                'size': 60,
            },
            {
                'type': 'receiver_cif',
                'value': str(partner_picking.vat),
                'size': 16,
            },
            {
                'type': 'receiver_person',
                'value': str(partner_name),
                'size': 60,
            },
            {
                'type': 'receiver_phone',
                'value': str(partner_phone),
                'size': 20,
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
                'type': 'observations',
                'value': str(observations),
                'size': 250,
            },
            {
                'type': 'order_number',
                'value': '',
                'size': 24,
            },
            {
                'type': 'date_deferred_delivery',
                'value': '',
                'size': 10,
            },
            {
                'type': 'maximum_delivery_date',
                'value': '',
                'size': 10,
            },
            {
                'type': 'reference_grouping',
                'value': '',
                'size': 24,
            },
            {
                'type': 'locator',
                'value': '',
                'size': 20,
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
                'type': 'sender_department',
                'value': '',
                'size': 60,
            },
            {
                'type': 'reference2',
                'value': '',
                'size': 35,
            },
            {
                'type': 'exit_date_set',
                'value': '',
                'size': 10,
            },
            {
                'type': 'refund_amount',
                #'value': '0000000.00',
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
            {
                'type': 'label_printer',
                'value': '',
                'size': 30,
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
            fh = open(file_name,'a')# if file does not exist, create it                            
            fh.write(txt_line)
            fh.close()
                    
            #upload ftp tsb (open port 21 outbound in security groups)
            ftp = ftplib.FTP(self.tsb_ftp_host)
            
            try:
                ftp.login(self.tsb_ftp_user, self.tsb_ftp_password)
            except ftplib.error_perm as e:
                os.remove(file_name)#Fix remove file previously generate
                
                response = {
                    'errors': True, 
                    'error': "Login incorrecto FTP TSB", 
                    'return': "",
                }
                return response
              
            ftp.cwd(self.tsb_ftp_directory_upload)
            f_h = open(file_name,'rb')
            ftp.storbinary('STOR ' + file_name_real, f_h)  
            ftp.quit()
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
        separator_fields = '|'
        #response
        response = {
            'errors': True, 
            'error': "", 
            'return': "",
        }                 
        #file_name ric
        file_name_real = "RIC_"+self.sender_customer+'.txt'
        file_name = os.path.dirname(os.path.abspath(__file__))+'/'+file_name_real
        #ftp + download
        ftp = ftplib.FTP(self.tsb_ftp_host)
        ftp.login(self.tsb_ftp_user, self.tsb_ftp_password)  
        ftp.cwd(self.tsb_ftp_directory_download)                
        
        ls = []
        ftp.retrlines('MLSD', ls.append)
        
        shipping_expedition_find = False
        
        for entry in ls:
            entry_split = entry.split(";")
            entry_name = str(entry_split[4])
            entry_name = entry_name.replace(" ", "")
            
            if entry_name!="." and entry_name!="..":                                
                ftp.retrbinary("RETR "+entry_name, open(file_name, 'wb').write)                                           
                #read_file        
                if os.path.isfile(file_name):
                    f = open(file_name, 'r')
                    for line in f:
                        if separator_fields in line:                           
                            line_split = line.split(separator_fields)                        
                            
                            expedition_line = line_split[0]                    
                            reference_line = line_split[1]
                            origin_line = line_split[15]
                            ctrl_identiticket_line = line_split[28]
                            ctrl_localizator_line = line_split[29]
                            ctrl_link_line = line_split[30]  
                            estd_fecha_llegada_line = line_split[33]
                            estd_codigo_situacion_line = line_split[36]
                            
                            if shipping_expedition.picking_id.name==reference_line and shipping_expedition_find==False:                                                                                                
                                estd_fecha_llegada_line_split = estd_fecha_llegada_line.split(' ')
                                estd_fecha_llegada_line2 = estd_fecha_llegada_line_split[0].split('/')
                                estd_fecha_llegada_line_real = estd_fecha_llegada_line2[2]+'-'+estd_fecha_llegada_line2[1]+'-'+estd_fecha_llegada_line2[0] 
                                
                                shipping_expedition.code = expedition_line
                                shipping_expedition.delivery_code = reference_line                    
                                shipping_expedition.tsb_identiticket = ctrl_identiticket_line
                                shipping_expedition.date = estd_fecha_llegada_line_real
                                shipping_expedition.tsb_localizator = ctrl_localizator_line
                                shipping_expedition.tsb_url = ctrl_link_line
                                #codigo_situacion
                                if estd_codigo_situacion_line!="00000001":
                                    if estd_codigo_situacion_line=="00000002":
                                        shipping_expedition.state = "shipped"
                                    elif estd_codigo_situacion_line=="00000003" or estd_codigo_situacion_line=="00000006":
                                        shipping_expedition.state = "in_transit"
                                    elif estd_codigo_situacion_line=="00000004":
                                        shipping_expedition.state = "in_delegation"                            
                                    elif estd_codigo_situacion_line=="00000005":                            
                                        shipping_expedition.state = "delivered"
                                    else:
                                        shipping_expedition.state = "incidence"
                                #result
                                response['return'] = {
                                    'label': "",                    
                                }
                                response['return']['result'] = {
                                    'expe_codigo': expedition_line,
                                    'fecha': estd_fecha_llegada_line_real,
                                    'estado_code': estd_codigo_situacion_line,
                                    'origen': origin_line,
                                    'albaran': reference_line,
                                    'exps_rels': "", 
                                }
                                
                                shipping_expedition_find = True                                
                                
        #response
        ftp.quit()
        response['errors'] = False                                                                                   
        return response                                      