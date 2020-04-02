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
    picking_id_type_code = fields.Char(
        compute='_get_picking_id_type_code',
        store=False
    )   
    pack_lot_ids_incoming = fields.One2many('stock.pack.operation.lot', 'operation_id', string='Lotes Entrada')
    pack_lot_ids_outgoing = fields.One2many('stock.pack.operation.lot', 'operation_id', string='Lotes Salida')
    pack_lot_ids_internal = fields.One2many('stock.pack.operation.lot', 'operation_id', string='Lotes Internos')                
    
    @api.multi
    def write(self, values):              
        if 'pack_lot_ids' not in values:
            #pack_lot_ids_incoming
            if 'pack_lot_ids_incoming' in values:
                values['pack_lot_ids'] = values.get('pack_lot_ids_incoming')
                values['pack_lot_ids_incoming'] = None
            #pack_lot_ids_outgoing                
            if 'pack_lot_ids_outgoing' in values:
                values['pack_lot_ids'] = values.get('pack_lot_ids_outgoing')
                values['pack_lot_ids_outgoing'] = None
            #pack_lot_ids_internal            
            if 'pack_lot_ids_internal' in values:
                values['pack_lot_ids'] = values.get('pack_lot_ids_internal')
                values['pack_lot_ids_internal'] = None        
        #return
        return super(StockPackOperation, self).write(values)               
    
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
    def _get_picking_id_type_code(self):                
        self.picking_id_type_code = self.picking_id.picking_type_id.code
        if self.id>0:
            stock_pack_operation_lot_ids = self.env['stock.pack.operation.lot'].search([('operation_id', '=', self.id)])
            self.pack_lot_ids_incoming = stock_pack_operation_lot_ids
            self.pack_lot_ids_outgoing = stock_pack_operation_lot_ids
            self.pack_lot_ids_internal = stock_pack_operation_lot_ids                                                                                                                                                                                                            