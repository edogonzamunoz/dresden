# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccounJournal(models.Model):
    _inherit = 'account.journal'

    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string='Tipo Documento')
