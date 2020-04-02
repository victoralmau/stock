# -*- coding: utf-8 -*-
from openerp import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class StockPackOperationLot(models.Model):
    _inherit = 'stock.pack.operation.lot'
    
    custom_field = fields.Char(
        compute='_get_lot_id_picking',        
    )                  
    lot_id_picking_incoming = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lotes Incoming',
    )
    lot_id_picking_outgoing = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lotes Outgoing',
    )
    lot_id_picking_internal = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lotes Internal',
    )   
    lot_it_product_qty = fields.Float( 
        compute='_get_lot_it_product_qty',
        string='Cantidad lote'
    )
    lot_it_picking_incoming_product_qty = fields.Float( 
        compute='_get_lot_it_picking_incoming_product_qty',
        string='Cantidad lote'
    )
    lot_it_picking_outgoing_product_qty = fields.Float( 
        compute='_get_lot_it_picking_outgoing_product_qty',
        string='Cantidad lote'
    )
    lot_it_picking_internal_product_qty = fields.Float( 
        compute='_get_lot_it_picking_internal_product_qty',
        string='Cantidad lote'
    )
    
    @api.model
    def create(self, values):
        if 'lot_id' not in values:     
            #lot_id_picking_incoming       
            if 'lot_id_picking_incoming' in values:
                values['lot_id'] = values.get('lot_id_picking_incoming')
            #lot_id_picking_outgoing
            if 'lot_id_picking_outgoing' in values:
                values['lot_id'] = values.get('lot_id_picking_outgoing')
            #lot_id_picking_internal
            if 'lot_id_picking_internal' in values:
                values['lot_id'] = values.get('lot_id_picking_internal')                                
        
        return_object = super(StockPackOperationLot, self).create(values)
        return return_object                                                    
        
    @api.one    
    @api.depends('lot_id.product_qty_store')    
    def _get_lot_it_product_qty(self):                
        self.lot_it_product_qty = 0
        if self.lot_id.id>0:
            self.lot_it_product_qty = self.lot_id.product_qty_store
    
    @api.one        
    def _get_lot_id_picking(self):
        if self.id>0 and self.lot_id.id>0:
            self.lot_id_picking_incoming = self.lot_id
            self.lot_id_picking_outgoing = self.lot_id
            self.lot_id_picking_internal = self.lot_id                            
                    
    @api.one    
    @api.depends('lot_id_picking_incoming.product_qty_store')    
    def _get_lot_it_picking_incoming_product_qty(self):                
        self.lot_it_picking_incoming_product_qty = 0
        if self.lot_id_picking_incoming.id>0:
            self.lot_it_picking_incoming_product_qty = self.lot_id_picking_incoming.product_qty_store
            
    @api.one    
    @api.depends('lot_id_picking_outgoing.product_qty_store')    
    def _get_lot_it_picking_outgoing_product_qty(self):                
        self.lot_it_picking_outgoing_product_qty = 0
        if self.lot_id_picking_outgoing.id>0:
            self.lot_it_picking_outgoing_product_qty = self.lot_id_picking_outgoing.product_qty_store
            
    @api.one    
    @api.depends('lot_id_picking_internal.product_qty_store')    
    def _get_lot_it_picking_internal_product_qty(self):                
        self.lot_it_picking_internal_product_qty = 0
        if self.lot_id_picking_internal.id>0:
            self.lot_it_picking_internal_product_qty = self.lot_id_picking_internal.product_qty_store                                                                                                                                                                                                 