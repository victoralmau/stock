# -*- coding: utf-8 -*-
from openerp import _, api, exceptions, fields, models

import logging
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'        

    s3_upload = fields.Boolean(
        string='S3 Upload'
    )
    s3_bucket = fields.Char(
        string='S3 Bucket'
    )
    s3_folder = fields.Char(
        string='S3 Folder'
    )
                                                                                               