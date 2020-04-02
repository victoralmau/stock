# -*- coding: utf-8 -*-
from openerp import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
                
    product_qty_store = fields.Float(     
        string='Cantidad Store'
    )
    
    @api.multi    
    def cron_odoo_stock_production_lot_product_qty_store(self, cr=None, uid=False, context=None):
        stock_production_lot_ids = self.env['stock.production.lot'].search([('id', '>', 0)])
        if stock_production_lot_ids!=False:
            for stock_production_lot_id in stock_production_lot_ids:                
                stock_quant_quantity_sum = 0 
                                   
                stock_quant_ids = self.env['stock.quant'].search(
                    [
                        ('product_id', '=', stock_production_lot_id.product_id.id),
                        ('lot_id', '=', stock_production_lot_id.id),
                        ('location_id.usage', '=', 'internal')
                    ]
                )                                
                if len(stock_quant_ids)>0:
                    for stock_quant_id in stock_quant_ids:
                        stock_quant_quantity_sum += stock_quant_id.qty
                        
                stock_production_lot_id.product_qty_store = stock_quant_quantity_sum           