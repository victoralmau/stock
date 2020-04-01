# -*- coding: utf-8 -*-
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
        string='Albaran'
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',        
        string='Pedido',
    )    
    user_id = fields.Many2one(
        comodel_name='res.users',        
        string='Comercial',
    )    
    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',        
        string='Transportista',
    )        
    carrier_type = fields.Char(
        string='Tipo de transportista',
        compute='_get_carrier_type',
        readonly=True,
        store=False
    )    
    
    @api.multi        
    def _get_carrier_type(self):         
        for obj in self:           
            obj.carrier_type = obj.carrier_id.carrier_type
    
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto'
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
    date_send_mail_info = fields.Datetime(
        string='Fecha email info' 
    )    
    
    @api.model
    def create(self, values):
        record = super(ShippingExpedition, self).create(values)                    
        #add partner_id follower
        if record.partner_id!=False and record.partner_id.id>0:
            reg = {
                'res_id': record.id,
                'res_model': record._name,
                'partner_id': record.partner_id.id,
                'subtype_ids': [(6, 0, [1])],
            }
            self.env['mail.followers'].create(reg)
        #add user_id follower
        if record.user_id!=False and record.user_id.id>0:
            mail_followers_ids_check = self.env['mail.followers'].search([('res_model', '=', record._name,),('res_id', '=', record.id),('partner_id', '=', record.user_id.partner_id.id)])
            if mail_followers_ids_check==False:
                reg = {
                    'res_id': record.id,
                    'res_model': record._name,
                    'partner_id': record.user_id.partner_id.id,
                    'subtype_ids': [(6, 0, [1])],                                              
                }
                self.env['mail.followers'].create(reg)
        #check remove create uid
        if record.user_id!=False and record.create_uid.id!=record.user_id.id:
            mail_followers_ids = self.env['mail.followers'].search([('res_model', '=', record._name,),('res_id', '=', record.id)])
            if mail_followers_ids!=False:
                for mail_follower_id in mail_followers_ids:
                    if mail_follower_id.partner_id.id==record.create_uid.partner_id.id:
                        #mail_follower_id.unlink()
                        self.env.cr.execute("DELETE FROM  mail_followers WHERE id = "+str(mail_follower_id.id))                                
                                                                
        return record
                  
    @api.one
    def update_state(self):
        return True
    
    @api.one
    def action_update_state(self):
        if self.state!="delivered":
            self.update_state()
                                 
        return True
    
    @api.one
    def cancel_state(self):
        return True    
    
    @api.one
    def action_cancell(self):
        if self.state!="canceled":
            self.cancel_state()
    
        return True
    
    @api.one    
    def action_error_update_state_expedition_message_slack(self, res):
        return
        
    @api.one    
    def action_incidence_expedition_message_slack(self, res):
        return
        
    @api.one    
    def action_error_cancell_expedition_message_slack(self, res):
        return
        
    @api.one    
    def action_send_mail_info_expedition_message_slack(self):
        return                                        
            
    @api.one
    def action_send_mail_info(self, template_id=False):
        if template_id!=False:
            states_skip = ['error', 'generate','canceled', 'delivered']
            if self.state not in states_skip:        
                if self.date_send_mail_info==False:
                    if self.delegation_name!=False and self.delegation_phone!=False:                    
                        mail_template_item = self.env['mail.template'].search([('id', '=', template_id)])[0]                                
                        mail_compose_message_vals = {                    
                            'author_id': self.user_id.partner_id.id,
                            'record_name': self.name,                                                                                                                                                                                           
                        }
                        mail_compose_message_obj = self.env['mail.compose.message'].with_context().sudo().create(mail_compose_message_vals)
                        return_onchange_template_id = mail_compose_message_obj.onchange_template_id(mail_template_item.id, 'comment', 'shipping.expedition', self.id)                                
                        
                        mail_compose_message_obj.update({
                            'author_id': mail_compose_message_vals['author_id'],
                            'template_id': mail_template_item.id,
                            'composition_mode': 'comment',
                            'model': 'shipping.expedition',
                            'res_id': self.id,
                            'body': return_onchange_template_id['value']['body'],
                            'subject': return_onchange_template_id['value']['subject'],
                            'email_from': return_onchange_template_id['value']['email_from'],
                            'partner_ids': return_onchange_template_id['value']['partner_ids'],
                            #'attachment_ids': return_onchange_template_id['value']['attachment_ids'],
                            'record_name': mail_compose_message_vals['record_name'],
                            'no_auto_thread': False,                     
                        })                                         
                        mail_compose_message_obj.send_mail_action()                                                        
                        self.date_send_mail_info = datetime.today()                        
                        self.action_send_mail_info_expedition_message_slack()#slack.message                        
                                            
            return True                                    