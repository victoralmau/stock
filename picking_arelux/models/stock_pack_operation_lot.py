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
    
    @api.multi
    def write(self, values):
        return_object = super(StockPackOperationLot, self).write(values)
        #operations
        if 'need_update_pack_lot_ids' not in values:
            for item in self:
                if item.operation_id.picking_id.picking_type_id.code=='incoming':
                    item.write({
                        'lot_id': item.lot_id_picking_incoming.id,
                        'name': item.lot_id_picking_incoming.name,
                        'need_update_pack_lot_ids': False
                    })
                elif item.operation_id.picking_id.picking_type_id.code=='outgoing':
                    item.write({
                        'lot_id': item.lot_id_picking_outgoing.id,
                        'name': item.lot_id_picking_incoming.name,
                        'need_update_pack_lot_ids': False
                    })
                elif item.operation_id.picking_id.picking_type_id.code=='internal':
                    item.write({
                        'lot_id': item.lot_id_picking_internal.id,
                        'name': item.lot_id_picking_incoming.name,
                        'need_update_pack_lot_ids': False
                    })                    
        #return
        return return_object            
            
    @api.one    
    @api.depends('lot_id.product_qty_store')    
    def _get_lot_it_product_qty(self):                
        self.lot_it_product_qty = 0
        if self.lot_id.id>0:
            self.lot_it_product_qty = self.lot_id.product_qty_store
    
    @api.one        
    def _get_lot_id_picking(self):
        _logger.info('_get_lot_id_picking')
                                
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