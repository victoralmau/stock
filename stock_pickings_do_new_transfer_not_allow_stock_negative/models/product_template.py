# -*- coding: utf-8 -*-
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)
                    
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_negative_stock = fields.Boolean(
        string='Permitir stock negativo'
    )
    
    @api.one
    def get_quantity_by_lot_id(self, lot_id=0):
        qty = 0
        
        if lot_id==0:
            stock_quant_ids = self.env['stock.quant'].sudo().search([('location_id', '=', 15),('product_id', '=', self.id)])
        else:
            stock_quant_ids = self.env['stock.quant'].sudo().search([('location_id', '=', 15),('product_id', '=', self.id),('lot_id', '=', lot_id)])
        #operations
        if len(stock_quant_ids)>0:
            for stock_quant_id in stock_quant_ids:
                qty += stock_quant_id.qty
                
        return qty        