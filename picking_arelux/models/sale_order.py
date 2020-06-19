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
                        if carrier_check in item.note or carrier_check.upper() in item.note:
                            delivery_carrier_ids = self.env['delivery.carrier'].search([('carrier_type', '=', carrier_check)])
                            for delivery_carrier_id in delivery_carrier_ids:
                                item.carrier_id = delivery_carrier_id.id
                #check  picking_note                   
                if item.picking_note!=False:
                    for carrier_check in carriers_check:        
                        if carrier_check in item.picking_note or carrier_check.upper() in item.picking_note:
                            delivery_carrier_ids = self.env['delivery.carrier'].search([('carrier_type', '=', carrier_check)])
                            for delivery_carrier_id in delivery_carrier_ids:
                                item.carrier_id = delivery_carrier_id.id
        #action_confirm                                                            
        return_data = super(SaleOrder, self).action_confirm()
        #operations
        for item in self:
            if item.state == 'sale':
                for picking_id in item.picking_ids:
                    #operations
                    if picking_id.carrier_id.id>0:
                        if picking_id.carrier_id.carrier_type=='nacex':
                            default_codes = []
                            for order_line in item.order_line:
                                if order_line.product_id.default_code!=False:
                                    if order_line.product_id.default_code not in default_codes:
                                        default_codes.append(str(order_line.product_id.default_code))
                            #only_prduct_MCH12
                            if len(default_codes)>0:
                                if len(default_codes)==1 and default_codes[0]=='MCH12':
                                    stock_picking_type_ids = self.env['stock.picking.type'].sudo().search([('sequence_id.code', '=', 'stock.picking.nacex.muestras')])
                                    if len(stock_picking_type_ids)>0:
                                        stock_picking_type_id = stock_picking_type_ids[0]
                                        picking_id.picking_type_id = stock_picking_type_id.id
                                        picking_id.name = self.env['ir.sequence'].next_by_code(self.env['stock.picking.type'].search([('id', '=', picking_id.picking_type_id.id)])[0].sequence_id.code)
        #return
        return return_data