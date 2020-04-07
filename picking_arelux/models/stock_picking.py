# -*- coding: utf-8 -*-
from openerp import api, models, fields
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

from lxml import etree

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    supplier_ref = fields.Char( 
        string='Referencia del proveedor',
        size=30
    )
    sale_order_note = fields.Char( 
        string='Nota pedido de venta',
    )
    shipping_expedition_note = fields.Char( 
        string='Nota pedido de venta expedicion',
    )
    partner_state_id = fields.Char(
        compute='_get_partner_state_id', 
        string='Provincia',
        store=True
    )    
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Pedido',
        copy=False
    )
    confirmation_date_order = fields.Datetime(
        string='Fecha confirmacion pedido',
        store=True
    )
    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Compra',
        copy=False
    )
    number_of_pallets = fields.Integer(
        string='Palets',
        default=1
    )
    user_id_done = fields.Many2one(
        comodel_name='res.users',
        string='Preparado por',
        copy=False
    )
    management_date = fields.Datetime(
        string='Fecha preparacion',
        copy=False, 
        readonly=True
    )
    out_refund_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Factura devolucion'
    )        
    
    @api.multi
    def force_assign(self):
        #operations
        for obj in self:
            if obj.group_id.id>0:
                procurement_order_ids = self.env['procurement.order'].sudo().search([('group_id', '=', obj.group_id.id)])
                if len(procurement_order_ids)>0:
                    procurement_order_id = procurement_order_ids[0]
                    #sale_line_id
                    if procurement_order_id.sale_line_id.id>0:
                        obj.order_id = procurement_order_id.sale_line_id.order_id.id
                        #confirmation_date_order
                        obj.confirmation_date_order = obj.order_id.confirmation_date
                    #purchase_line_id
                    if procurement_order_id.purchase_line_id.id>0:
                        obj.purchase_id = procurement_order_id.purchase_line_id.order_id.id                                                                     
        #return
        return super(StockPicking, self).force_assign()
    
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):        
        res = super(StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)                        
                                
        if view_type == 'tree':            
            default_picking_type_id = self.env.context.get('default_picking_type_id')                        
            doc = etree.fromstring(res['arch'])
            
            if default_picking_type_id!=1:
                #fields_invisible = ['date', 'min_date']
                fields_invisible = ['date']
                
                fields = doc.findall('field')
                for field in fields:
                    field_name = field.get('name')
                    if field_name in fields_invisible:
                        #field.set('invisible', '1')
                        doc.remove(field)                    
            else:
                doc.set('default_order', 'min_date asc')
                
                fields_invisible = ['carrier_id', 'shipping_expedition_id', 'management_date', 'confirmation_date_order', 'user_id_done', 'date']
                
                fields = doc.findall('field')
                for field in fields:
                    field_name = field.get('name')
                    if field_name in fields_invisible:
                        doc.remove(field)
            
            res['arch'] = etree.tostring(doc)                                                    
                                                                    
        return res    
    
    @api.one
    def do_transfer(self):
        return_super = super(StockPicking, self).do_transfer()
        if return_super==True:
            if len(self.pack_operation_product_ids)>0:
                for pack_operation_product_id in self.pack_operation_product_ids:
                    if pack_operation_product_id.product_id.id>0 and pack_operation_product_id.product_id.tracking=='lot':
                        if len(pack_operation_product_id.pack_lot_ids)>0:
                            for pack_lot_id in pack_operation_product_id.pack_lot_ids:
                                if pack_lot_id.lot_id.id>0:
                                    stock_quant_quantity_sum = 0 
                                                                                                                   
                                    stock_quant_ids = self.env['stock.quant'].search(
                                        [
                                            ('product_id', '=', pack_operation_product_id.product_id.id),
                                            ('lot_id', '=', pack_lot_id.lot_id.id),
                                            ('location_id.usage', '=', 'internal')
                                        ]
                                    )                
                                    if len(stock_quant_ids)>0:
                                        for stock_quant_id in stock_quant_ids:
                                            stock_quant_quantity_sum += stock_quant_id.qty
                                                                                                                        
                                    pack_lot_id.lot_id.product_qty_store = stock_quant_quantity_sum 
        #return            
        return return_super       
    
    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        for obj in self:
            if obj.state=='done' and obj.user_id_done.id==0:                                
                obj.user_id_done = obj.env.uid#Id actual
        #return
        return super(StockPicking, self)._create_backorder(backorder_moves)                       
    
    @api.model
    def create(self, vals):
        nacex_samples = False
        if 'origin' in vals:                   
            sale_order_ids = self.env['sale.order'].search([('name', '=', str(vals['origin']))])
            if len(sale_order_ids)>0:
                for sale_order_id in sale_order_ids:
                    #Fix nacex
                    if sale_order_id.carrier_id.id!=False:
                        if sale_order_id.carrier_id.carrier_type=='nacex':
                            for order_line in sale_order_id.order_line:
                                if order_line.product_id.id==97:
                                    nacex_samples = True                                                                        
                                    
        if nacex_samples==True:
            ptype_id = 7                            
            vals['name'] = self.env['ir.sequence'].next_by_code(self.env['stock.picking.type'].search([('id', '=', ptype_id)])[0].sequence_id.code)
            vals['picking_type_id'] = ptype_id                    
        #return
        return super(StockPicking, self).create(vals)        
    
    @api.multi        
    def _get_partner_state_id(self):
        for obj in self:
            obj.partner_state_id = ''
            if obj.partner_id.id>0:
                if obj.partner_id.state_id.id>0:
                    obj.partner_state_id = obj.partner_id.state_id.name                        
                        
    @api.multi
    def _add_delivery_cost_to_so(self):
        for obj in self:
            if obj.sale_id.id>0:        
                sale_order = obj.sale_id
                if obj.carrier_id.id>0:
                    sale_order.carrier_id = obj.carrier_id.id
        #return            
        return super(StockPicking, self)._add_delivery_cost_to_so()
        
    @api.one    
    def action_send_account_invoice_out_refund(self):
        return False
    
    @api.multi    
    def cron_operations_autogenerate_invoices_stock_picking_return(self, cr=None, uid=False, context=None):        
        current_date = datetime.today()
        allow_generate_invoices = True
        
        if current_date.day==31 and current_date.month==12:
            allow_generate_invoices = False
            
        if current_date.day==1 and current_date.month==1:
            allow_generate_invoices = False
        
        if allow_generate_invoices==True:
            stock_picking_ids = self.env['stock.picking'].search(
                [
                    ('id', '>', 125958),
                    ('picking_type_id', '=', 6),                    
                    ('state', '=', 'done'),
                    ('out_refund_invoice_id', '=', False) 
                 ]
            )
            if len(stock_picking_ids)>0:
                for stock_picking_id in stock_picking_ids:
                    stock_picking_ids_get = self.env['stock.picking'].search(
                        [
                            ('picking_type_id', '!=', 6),
                            ('state', '=', 'done'),
                            ('name', '=', stock_picking_id.origin)
                        ]
                    )
                    if len(stock_picking_ids_get)>0:
                        stock_picking_id_origin = stock_picking_ids_get[0] 
                        if stock_picking_id_origin.order_id.id>0:                                                        
                            #check exist crm_claim (not need generate account.invoice automatic)
                            need_create_out_invoice = True
                            crm_claim_ids_get = self.env['crm.claim'].search(
                                [
                                    ('active', '=', True),
                                    ('model_ref_id', '=', 'sale.order,'+str(stock_picking_id_origin.order_id.id))                                    
                                ]
                            )                            
                            if len(crm_claim_ids_get)>0:
                                need_create_out_invoice = False                            
                            
                            if need_create_out_invoice==True:
                                if stock_picking_id_origin.order_id.invoice_status=='invoiced':
                                    if len(stock_picking_id_origin.order_id.invoice_ids)>0:
                                        #invoice_id
                                        invoice_id = False
                                        for invoice_id_get in stock_picking_id_origin.order_id.invoice_ids:
                                            if invoice_id_get.type=='out_invoice':
                                                invoice_id = invoice_id_get                                                                        
                                        #contionue
                                        if invoice_id!=False:
                                            #products_info
                                            products_info = {}
                                            for invoice_line_id in invoice_id.invoice_line_ids:
                                                if invoice_line_id.product_id.id>0:
                                                    products_info[invoice_line_id.product_id.id] = {
                                                        'name': invoice_line_id.name,
                                                        'price_unit': invoice_line_id.price_unit,
                                                        'account_id': invoice_line_id.account_id.id,
                                                        'discount': invoice_line_id.discount,
                                                    }                                                                                                                                                                                                
                                            #account.invoice
                                            account_invoice_vals = {
                                                'partner_id': invoice_id.partner_id.id,
                                                'partner_shipping_id': invoice_id.partner_shipping_id.id,
                                                'account_id': invoice_id.account_id.id,
                                                'journal_id': invoice_id.journal_id.id,
                                                'state': 'draft',
                                                'type': 'out_refund',
                                                'comment': ' ',
                                                'origin': invoice_id.number,
                                                'name': stock_picking_id.name,
                                                'ar_qt_activity_type': invoice_id.ar_qt_activity_type,
                                                'ar_qt_customer_type': invoice_id.ar_qt_customer_type,
                                                'payment_mode_id': invoice_id.payment_mode_id.id,
                                                'payment_term_id': invoice_id.payment_term_id.id,
                                                'fiscal_position_id': invoice_id.fiscal_position_id.id,
                                                'team_id': invoice_id.team_id.id,
                                                'user_id': invoice_id.user_id.id                                          
                                            }
                                            #partner_bank_id
                                            if invoice_id.partner_bank_id.id>0:
                                                account_invoice_vals['partner_bank_id'] = invoice_id.partner_bank_id.id 
                                            #mandate_id
                                            if invoice_id.mandate_id.id>0:
                                                account_invoice_vals['mandate_id'] = invoice_id.mandate_id.id
                                            #create
                                            account_invoice_obj = self.env['account.invoice'].sudo().create(account_invoice_vals)
                                            #lines
                                            for pack_operation_product_id in stock_picking_id.pack_operation_product_ids:
                                                account_invoice_line_vals = {
                                                    'invoice_id': account_invoice_obj.id,
                                                    'product_id': pack_operation_product_id.product_id.id,
                                                    'quantity': pack_operation_product_id.qty_done,
                                                    'price_unit': products_info[pack_operation_product_id.product_id.id]['price_unit'],
                                                    'discount': products_info[pack_operation_product_id.product_id.id]['discount'],
                                                    'account_id': products_info[pack_operation_product_id.product_id.id]['account_id'],
                                                    'name': products_info[pack_operation_product_id.product_id.id]['name']                     
                                                }
                                                account_invoice_line_obj = self.env['account.invoice.line'].sudo().create(account_invoice_line_vals)
                                                account_invoice_line_obj._onchange_product_id()
                                                account_invoice_line_obj._onchange_account_id()
                                                #price
                                                price_unit_clean = account_invoice_line_vals['price_unit']
                                                
                                                if account_invoice_line_vals['discount']>0:
                                                    price_unit_discount = (account_invoice_line_vals['price_unit']/100)*account_invoice_line_vals['discount']
                                                    price_unit_clean = account_invoice_line_vals['price_unit']-price_unit_discount
                                                
                                                price_subtotal = price_unit_clean*account_invoice_line_vals['quantity']
                                                                                            
                                                account_invoice_line_obj.update({
                                                    'price_unit': round(account_invoice_line_vals['price_unit'],4),
                                                    'price_subtotal': round(price_subtotal,4),
                                                })
                                            #compute_taxes                                                                                    
                                            account_invoice_obj.compute_taxes()
                                            account_invoice_obj.action_invoice_open()
                                            #update_stock_picking
                                            stock_picking_id.out_refund_invoice_id = account_invoice_obj.id
                                            #action_send_account_invoice_out_refund
                                            stock_picking_id.action_send_account_invoice_out_refund()                                                                                                                                                                                                                                                                                                                                                                                                                            