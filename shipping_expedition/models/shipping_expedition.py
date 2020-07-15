# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class ShippingExpedition(models.Model):
    _name = 'shipping.expedition'
    _description = 'Shipping Expedicion'
    _inherit = ['mail.thread']
    
    name = fields.Char(        
        compute='_get_name',
        string='Nombre',
        store=False
    )
    
    @api.one        
    def _get_name(self):            
        for obj in self:
            obj.name = obj.delivery_code
    
    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Albaran',
        required=True
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Pedido',
        related='picking_id.sale_id',
        store=False,
        readonly=True
    )
    lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Lead',
        related='picking_id.sale_id.opportunity_id',
        store=False,
        readonly=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',        
        string='Comercial',
        related='picking_id.sale_id.user_id',
        store=False,
        readonly=True
    )    
    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',        
        string='Transportista',
        related='picking_id.carrier_id',
        store=False,
        readonly=True
    )        
    carrier_type = fields.Selection(
        string='Tipo de transportista',
        related='picking_id.carrier_id.carrier_type',
        store=False,
        readonly=True
    )
    
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        related='picking_id.partner_id',
        store=False,
        readonly=True
    )    
    code = fields.Char(
        string='Codigo expedicion'
    )
    delivery_code = fields.Char(
        string='Codigo albaran'
    )             
    date = fields.Date(
        string='Fecha'
    )    
    hour = fields.Char(
        string='Hora'
    )
    observations = fields.Text(
        string='Observaciones'
    )
    state = fields.Selection(
        selection=[
            ('error','Error'), 
            ('generate','Generado'), 
            ('shipped','Enviado'), 
            ('in_delegation','En delegacion'), 
            ('incidence','Incidencia'), 
            ('in_transit','En reparto'), 
            ('delivered','Entregado'),
            ('canceled','Anulada'),
        ],
        string='Estado'
    )
    state_code = fields.Char(
        string='Codigo estado'
    )
    origin = fields.Char(
        string='Origen'
    )
    delivery_note = fields.Char(
        string='Nota de entrega'
    )
    exps_rels = fields.Char(
        string='Expediciones relacionadas'
    )
    delegation_name = fields.Char(
        string='Nombre delegacion'
    )
    delegation_phone = fields.Char(
        string='Telefono delegacion'
    )
    url_info = fields.Char(
        string='Url info'
    )
    ir_attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Adjunto'
    )            
    
    @api.model
    def create(self, values):
        record = super(ShippingExpedition, self).create(values)
        # add partner_id follower
        if record.partner_id.id > 0:
            reg = {
                'res_id': record.id,
                'res_model': 'shipping.expedition',
                'partner_id': record.partner_id.id,
                'subtype_ids': [(6, 0, [1])],
            }
            self.env['mail.followers'].create(reg)
        # add user_id follower
        if record.user_id.id > 0:
            mail_followers_ids_check = self.env['mail.followers'].search(
                [
                    ('res_model', '=', 'shipping.expedition'),
                    ('res_id', '=', record.id),
                    ('partner_id', '=', record.user_id.partner_id.id)
                ]
            )
            if len(mail_followers_ids_check) == 0:
                reg = {
                    'res_id': record.id,
                    'res_model': 'shipping.expedition',
                    'partner_id': record.user_id.partner_id.id,
                    'subtype_ids': [(6, 0, [1])],                                              
                }
                self.env['mail.followers'].create(reg)
        # check remove create uid
        if record.user_id.id > 0:
            if record.user_id.id!=record.create_uid.id:
                mail_followers_ids = self.env['mail.followers'].search(
                    [
                        ('res_model', '=', 'shipping.expedition'),
                        ('res_id', '=', record.id)
                    ]
                )
                if mail_followers_ids != False:
                    for mail_follower_id in mail_followers_ids:
                        if mail_follower_id.partner_id.id==record.create_uid.partner_id.id:
                            mail_follower_id.sudo().unlink()
        # record
        return record
    
    @api.multi    
    def cron_shipping_expeditions_update_state(self, cr=None, uid=False, context=None):
        current_date = datetime.today()
        
        shipping_expedition_ids = self.env['shipping.expedition'].search(
            [
                ('state', 'not in', ('delivered', 'canceled')),
                ('carrier_id.carrier_type', 'in', ('cbl', 'txt', 'tsb', 'nacex')),
                ('date', '<', current_date.strftime("%Y-%m-%d"))
            ]
        )
        if len(shipping_expedition_ids)>0:                
            for shipping_expedition_id in shipping_expedition_ids:
                shipping_expedition_id.action_update_state()
                
    @api.one
    def action_update_state(self):
        return False        
    
    @api.one    
    def action_error_update_state_expedition(self, res):
        return                                    