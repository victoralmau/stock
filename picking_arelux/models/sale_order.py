# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    picking_note = fields.Char( 
        string='Nota albaran',
    )
    shipping_expedition_note = fields.Char( 
        string='Nota expedicion',
    )
    picking_priority = fields.Selection(
        [
            ('0', 'No urgente'),
            ('1', 'Normal'),
            ('2', 'Urgente'),
            ('3', 'Muy Urgente'),        
        ],
        default='1',        
        string='Prioridad albaran',
    ) 
    
    def _create_delivery_line(self, carrier, price_unit):
        if price_unit>0:
            return super(SaleOrder, self)._create_delivery_line(carrier, price_unit)               
    
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
        #action_confirm                                                            
        return_data =  super(SaleOrder, self).action_confirm()
        if return_data==True:        
            for obj in self:
                for picking_id in obj.picking_ids:
                    picking_id.sale_order_note = obj.picking_note
                    picking_id.shipping_expedition_note = obj.shipping_expedition_note
                    picking_id.priority = obj.picking_priority                
        #return
        return return_data                                                                                                                                       