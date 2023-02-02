from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _default_boleta_journal(self):
        return self.env['account.journal'].search(
            [('type', '=', 'sale'), ('code', '=', 'BOL')], limit=1)

    pos_boleta_journal_id = fields.Many2one(
        'account.journal', string='Boleta Journal',
        domain=[('type', '=', 'sale')],
        help="Accounting journal used to create Boleta.",
        default=_default_boleta_journal)
