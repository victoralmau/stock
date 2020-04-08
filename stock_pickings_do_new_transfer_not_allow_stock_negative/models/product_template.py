# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)
                    
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_negative_stock = fields.Boolean(
        string='Permitir stock negativo'
    )
    
    @api.one
    def get_quantity_by_serial_number(self, serial_number=False):
        qty = 0
        if serial_number==False:
            stock_history_ids = self.env['stock.history'].sudo().search([('product_id', '=', self.id)])
        else:
            stock_history_ids = self.env['stock.history'].sudo().search([('product_id', '=', self.id),('serial_number', '=', serial_number)])
        
        if len(stock_history_ids)>0:            
            for stock_history_id in stock_history_ids:
                qty += stock_history_id.quantity
                
        return qty        