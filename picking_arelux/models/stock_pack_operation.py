# -*- coding: utf-8 -*-
from openerp import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'
    
    name = fields.Char( 
        compute='_get_name',
        string='Descripcion',
        store=False
    )
    qty_to_lot_id_domain = fields.Float( 
        compute='_get_qty_to_lot_id_domain'
    )    
    
    
    @api.one        
    def _get_name(self):
        self.name = self.product_id.name
        
        if self.picking_id.id>0:            
            if self.picking_id.order_id.id>0:
                for order_line in self.picking_id.order_id.order_line:
                    if order_line.product_id.id==self.product_id.id:
                        self.name = order_line.name
            elif self.picking_id.purchase_id.id>0:
                for order_line in self.picking_id.purchase_id.order_line:
                    if order_line.product_id.id==self.product_id.id:
                        self.name = order_line.name
                        
    @api.one        
    def _get_qty_to_lot_id_domain(self):
        if self.picking_id.picking_type_id.code in ['outgoing', 'internal']:
            #regenerate_stock_production_lot_product_qty_store
            self.product_id.regenerate_stock_production_lot_product_qty_store()
            #define
            self.qty_to_lot_id_domain = self.product_qty
        else:
            self.qty_to_lot_id_domain = -300                        