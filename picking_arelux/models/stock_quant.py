# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    lot_ref = fields.Char( 
        string='Referencia interna',
        compute='_get_lot_ref',
        store=False
    )
    
    @api.one        
    def _get_lot_ref(self):
        for stock_quant in self:                              
            stock_quant.lot_ref = stock_quant.lot_id.ref                                                                                                                   