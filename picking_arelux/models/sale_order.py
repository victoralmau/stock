# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def action_confirm(self):
        #operations
        for item in self:
            if item.carrier_id.id==0:
                carriers_check = ['cbl', 'txt', 'tsb']            
                #check note
                if item.note!=False:
                    for carrier_check in carriers_check:        
                        if carrier_check in item.note or carrier_check.upper() in obj.note:
                            delivery_carrier_ids = self.env['delivery.carrier'].search([ ('carrier_type', '=', carrier_check)])                            
                            for delivery_carrier_id in delivery_carrier_ids:
                                item.carrier_id = delivery_carrier_id.id
                #check  picking_note                   
                if item.picking_note!=False:
                    for carrier_check in carriers_check:        
                        if carrier_check in item.picking_note or carrier_check.upper() in obj.picking_note:
                            delivery_carrier_ids = self.env['delivery.carrier'].search([ ('carrier_type', '=', carrier_check)])                            
                            for delivery_carrier_id in delivery_carrier_ids:
                                item.carrier_id = delivery_carrier_id.id
        #action_confirm                                                            
        return_data = super(SaleOrder, self).action_confirm()
        #operations
        for item in self:
            if item.state == 'sale':
                for picking_id in item.picking_ids:
                    if item.external_sale_order_id.id > 0:
                        if item.external_sale_order_id.external_source_id.id > 0:
                            for picking_id in item.picking_ids:
                                if picking_id.picking_type_id.id != item.external_sale_order_id.external_source_id.external_sale_order_picking_type_id.id:
                                    picking_id.picking_type_id = item.external_sale_order_id.external_source_id.external_sale_order_picking_type_id.id
                                    picking_id.name = self.env['ir.sequence'].next_by_code(self.env['stock.picking.type'].search([('id', '=', picking_id.picking_type_id.id)])[0].sequence_id.code)
                    else:
                        #Fix nacex
                        nacex_samples = False
                        if picking_id.carrier_id.id>0:
                            if picking_id.carrier_id.carrier_type=='nacex':
                                for order_line in item.order_line:
                                    if order_line.product_id.id==97:
                                        nacex_samples = True
                        #nacex_samples
                        if nacex_samples==True:
                            picking_id.picking_type_id = 7
                            picking_id.name = self.env['ir.sequence'].next_by_code(self.env['stock.picking.type'].search([('id', '=', picking_id.picking_type_id.id)])[0].sequence_id.code)
        #return
        return return_data