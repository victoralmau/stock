# -*- coding: utf-8 -*-
# © 2013 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, exceptions, fields, models

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'        

    estimated_cost = fields.Float(
        compute='_get_estimated_cost',
        string='Coste estimado',
        store=False
    )
    
    @api.one       
    def _get_estimated_cost(self):
        best_price = 0
        
        if self.picking_type_id.code=="outgoing" and self.shipping_expedition_id.id==False:
            #check change carrier
            old_carrier_id = self.carrier_id.id
            new_carrier_id = 0
                     
            if old_carrier_id==False:
                #search and change carrier_id
                if self.partner_id.id>0:
                    if self.partner_id.state_id.id>0:
                        carrier_id_best_price = 0
                        best_price = 0
                                 
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
                                carrier_id_best_price = delivery_carrier_range_ids[0].carrier_id.id
                                
                        if carrier_id_best_price>0:
                            new_carrier_id = carrier_id_best_price
                #search lines and change carrier_id                
                if self.move_lines!=False:
                    new_carrier_id_override = False
                    max_quantity_line_override = 0
                    
                    for move_line in self.move_lines:
                        if move_line.product_id.carrier_id.id>0:
                            if new_carrier_id_override==False:
                                new_carrier_id_override = move_line.product_id.carrier_id.id
                                max_quantity_line_override = move_line.weight
                            else:
                                if move_line.weight>max_quantity_line_override:
                                    new_carrier_id_override = move_line.product_id.carrier_id.id
                                    max_quantity_line_override = move_line.weight
                    
                    if new_carrier_id_override!=False:
                        new_carrier_id = new_carrier_id_override
                #change carrier_id if need                        
                if new_carrier_id>0:
                    self.write({'carrier_id': new_carrier_id})                                                                                                                                                                          
            #get_price
            if old_carrier_id>0:
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
                
                best_price = 0
                for delivery_carrier_range_id in delivery_carrier_range_ids:
                    if best_price==0:
                        best_price = delivery_carrier_range_id.price
                                                
        self.estimated_cost = best_price                                