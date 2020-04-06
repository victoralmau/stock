# -*- coding: utf-8 -*-
from openerp import _, api, exceptions, fields, models

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'        

    nacex_del_cli = fields.Char(
        string='Delegacion cliente'
    )
    nacex_num_cli = fields.Char(
        string='Numero cliente'
    )
    nacex_dep_cli = fields.Char(
        string='Departamento cliente'
    )    
    nacex_tip_ser = fields.Selection(
        selection=[
            ('02','02 - NACEX 12:00H'), 
            ('04','04 - PLUS BAG'), 
            ('08','NACEX 19:00H'), 
            ('09','09 - PUENTE URBANO'), 
            ('11','11 - NACEX 08:30H'), 
            ('20','20 - NACEX MALLORCA MARÍTIMO'), 
            ('21','21 - NACEX SABADO'),
            ('26','26 - PLUS PACK'),
            ('27','27 - E-NACEX')
        ],
        string='Tipo servicio'
    )    
    nacex_tip_cob = fields.Selection(
        selection=[
            ('O','O - Origen'), 
            ('D','D -  Destino'), 
            ('T','T - Tercera')             
        ],
        string='Tipo cobro'
    )
    nacex_tip_env = fields.Selection(
        selection=[
            ('0','0 - DOCS'), 
            ('1','1 - BAG'), 
            ('2','2 - PAQ')             
        ],
        string='Tipo envio'
    )
    nacex_print_model = fields.Char(
        string='Modelo impresora'
    )
    nacex_print_et = fields.Char(
        string='Modelo etiquetadora'
    )                                                                                       