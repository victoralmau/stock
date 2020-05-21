# -*- coding: utf-8 -*-
from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def action_confirm(self):
        #operations
        for obj in self:
            if obj.carrier_id.id==0:
                carriers_check = ['cbl', 'txt', 'tsb']            
                #check note
                if obj.note!=False:
                    for carrier_check in carriers_check:        
                        if carrier_check in obj.note or carrier_check.upper() in obj.note:                                                                
                            delivery_carrier_ids = self.env['delivery.carrier'].search([ ('carrier_type', '=', carrier_check)])                            
                            for delivery_carrier_id in delivery_carrier_ids:
                                obj.carrier_id = delivery_carrier_id.id
                #check  picking_note                   
                if obj.picking_note!=False:
                    for carrier_check in carriers_check:        
                        if carrier_check in obj.picking_note or carrier_check.upper() in obj.picking_note:
                            delivery_carrier_ids = self.env['delivery.carrier'].search([ ('carrier_type', '=', carrier_check)])                            
                            for delivery_carrier_id in delivery_carrier_ids:
                                obj.carrier_id = delivery_carrier_id.id
        # action_confirm
        return_data = super(SaleOrder, self).action_confirm()
        # operations
        for item in self:
            if item.state == 'sale':
                for picking_id in item.picking_ids:
                    # Fix nacex
                    nacex_samples = False
                    if picking_id.carrier_id.id > 0:
                        if picking_id.carrier_id.carrier_type == 'nacex':
                            for order_line in item.order_line:
                                if order_line.product_id.id == 97:
                                    nacex_samples = True
                    # nacex_samples
                    if nacex_samples == True:
                        picking_id.picking_type_id = 7
                        picking_id.name = self.env['ir.sequence'].next_by_code(self.env['stock.picking.type'].search([('id', '=', picking_id.picking_type_id.id)])[0].sequence_id.code)
        #return
        return return_data                                                                                                                                       