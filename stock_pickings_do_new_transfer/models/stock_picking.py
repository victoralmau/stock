# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, fields, models

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.model    
    def cron_stock_pickings_do_new_transfer(self):
        stock_pickings_do_new_transfer_picking_type_id = int(self.env['ir.config_parameter'].sudo().get_param('stock_pickings_do_new_transfer_picking_type_id'))
        
        stock_picking_ids = self.env['stock.picking'].search(
            [
                ('picking_type_id', '=', stock_pickings_do_new_transfer_picking_type_id),
                ('state', 'in', ('confirmed', 'partial_available', 'assigned'))
            ]
        )
        if stock_picking_ids!=False:                
            for stock_picking_id in stock_picking_ids:
                stock_picking_id.do_transfer()