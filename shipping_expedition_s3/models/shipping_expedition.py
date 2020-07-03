# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import _, api, exceptions, fields, models
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

import os

class ShippingExpedition(models.Model):
    _inherit = 'shipping.expedition'        
            
    @api.model
    def create(self, values):                            
        #create            
        return_object = super(ShippingExpedition, self).create(values)
        #operations
        if return_object.carrier_id.s3_upload==True:            
            return_object.upload_file_to_s3()
        #return                      
        return return_object
        
    @api.one
    def upload_file_to_s3(self):
        if self.carrier_id.s3_upload==True:
            #open file for reading
            picking_name_replace = self.picking_id.name.replace("/", "-")
            file_name_real = str(picking_name_replace)+'.txt'
            #folder_name
            folder_name = str(os.path.abspath(__file__))
            folder_name = folder_name.replace('_s3/models/shipping_expedition.py', '_'+str(self.carrier_id.carrier_type)+'/'+str(self.carrier_id.carrier_type))
            file_name_final =  str(folder_name)+'/'+str(file_name_real)                    
            #check if exists line
            if os.path.isfile(file_name_final):
                destination_filename = str(self.carrier_id.s3_folder)+str(file_name_real)            
                return_upload_to_s3 = self.env['s3.model'].sudo().upload_to_s3(file_name_final, destination_filename, self.carrier_id.s3_bucket, True)
                if return_upload_to_s3==False:
                    _logger.info("Error al copiar el archivo en S3")
            else:  
                _logger.info("MUY RARO, el archivo no existe ("+str(file_name_final)+')')                                            
                                                                                                                                                                                