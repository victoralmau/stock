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
        if len(stock_production_lot_ids)>0:
            product_ids = stock_production_lot_ids.mapped('product_id')
            if len(product_ids)>0:
                for product_id in product_ids:
                    product_id.regenerate_stock_production_lot_product_qty_store()                           