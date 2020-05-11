# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'        

    estimated_cost = fields.Float(
        string='Coste estimado',
        store=True
    )
    
    @api.multi
    def action_confirm(self):
        return_action = super(StockPicking, self).action_confirm()
        #operations
        for obj in self:
            if obj.picking_type_id.code=='outgoing':
                #get_carrier_id_cheaper
                if obj.carrier_id.id==0 and obj.partner_id.id>0:
                    obj.get_carrier_id_cheaper()
                #define_estimated_cost
                obj.define_estimated_cost()
        #return
        return return_action
        
    @api.onchange('carrier_id')
    def onchange_carrier_id_override(self):
        if self.carrier_id.id>0 and self.picking_type_id.code=='outgoing' and self.partner_id.id>0:
            if self.partner_id.country_id.id>0 and self.partner_id.state_id.id>0:
                self.define_estimated_cost()
    
    @api.one       
    def define_estimated_cost(self):
        if self.carrier_id.id>0 and self.partner_id.id>0:
            if self.partner_id.country_id.id>0 and self.partner_id.state_id.id>0:
                delivery_carrier_range_ids = self.env['delivery.carrier.range'].search(
                    [
                        ('country_id', '=', self.partner_id.country_id.id),
                        ('carrier_id', '=', self.carrier_id.id), 
                        ('weight_range_start', '>=', self.weight), 
                        '|', 
                        ('state_id', '=', False), 
                        ('state_id', '=', self.partner_id.state_id.id)
                    ]            
                )
                if len(delivery_carrier_range_ids)>0:
                    best_price = 0
                    for delivery_carrier_range_id in delivery_carrier_range_ids:
                        if best_price==0:
                            best_price = delivery_carrier_range_id.price
                    #update
                    self.estimated_cost = best_price
    
    @api.one       
    def get_carrier_id_cheaper(self):
        if self.carrier_id.id==0 and self.picking_type_id.code=='outgoing' and self.partner_id.id>0:
            if self.partner_id.country_id.id>0 and self.partner_id.state_id.id>0:
                #define
                best_price = 0
                new_carrier_id = 0                     
                #search and change carrier_id
                if self.partner_id.id>0:
                    carrier_id_best_price = 0
                    #with_state_id    
                    if self.partner_id.state_id.id>0:                                         
                        delivery_carrier_range_ids = self.env['delivery.carrier.range'].search(
                            [
                                ('country_id', '=', self.partner_id.country_id.id), 
                                ('weight_range_start', '>=', self.weight), 
                                '|', 
                                ('state_id', '=', False), 
                                ('state_id', '=', self.partner_id.state_id.id)
                            ]                        
                        )
                        if len(delivery_carrier_range_ids)>0:                                                        
                            for delivery_carrier_range_id in delivery_carrier_range_ids:
                                if best_price==0 or delivery_carrier_range_id.price<best_price:
                                    best_price = delivery_carrier_range_id.price
                                    carrier_id_best_price = delivery_carrier_range_id.carrier_id.id
                    else:
                        #get first without state_id
                        delivery_carrier_range_ids = self.env['delivery.carrier.range'].search(
                            [
                                ('country_id', '=', self.partner_id.country_id.id), 
                                ('weight_range_end', '>=', self.weight), 
                                ('state_id', '=', False)
                            ]                        
                        )
                        if len(delivery_carrier_range_ids)>0:
                            delivery_carrier_range_id = delivery_carrier_range_ids[0]
                            carrier_id_best_price = delivery_carrier_range_id.carrier_id.id
                    
                    #carrier_id_best_price                        
                    if carrier_id_best_price>0:
                        new_carrier_id = carrier_id_best_price
                        self.carrier_id = new_carrier_id                                            