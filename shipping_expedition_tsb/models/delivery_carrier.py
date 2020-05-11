# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'        

    tsb_sender_customer = fields.Char(
        string='Tsb sender customer'
    )
    tsb_sender_center = fields.Char(
        string='Tsb sender center'
    )
    tsb_ftp_host = fields.Char(
        string='Tsb Ftp host'
    )
    tsb_ftp_user = fields.Char(
        string='Tsb Ftp user'
    )
    tsb_ftp_password = fields.Char(
        string='Tsb Ftp password'
    )
    tsb_ftp_directory_upload = fields.Char(
        string='Tsb Ftp directory upload'
    )
    tsb_ftp_directory_download = fields.Char(
        string='Tsb Ftp directory download'
    )                                                                             