from odoo import fields, models, api
from functools import partial

class PosOrder(models.Model):
    _inherit = 'pos.order'

    to_boleta = fields.Boolean('To boleta', copy=False)

    @api.model
    def _order_fields(self, ui_order):
        process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
        return {
            'user_id': ui_order['user_id'] or False,
            'session_id': ui_order['pos_session_id'],
            'lines': [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
            'pos_reference': ui_order['name'],
            'sequence_number': ui_order['sequence_number'],
            'partner_id': ui_order['partner_id'] or False,
            'date_order': ui_order['creation_date'].replace('T', ' ')[:19],
            'fiscal_position_id': ui_order['fiscal_position_id'],
            'pricelist_id': ui_order['pricelist_id'],
            'amount_paid': ui_order['amount_paid'],
            'amount_total': ui_order['amount_total'],
            'amount_tax': ui_order['amount_tax'],
            'amount_return': ui_order['amount_return'],
            'company_id': self.env['pos.session'].browse(ui_order['pos_session_id']).company_id.id,
            'to_invoice': ui_order['to_invoice'] if "to_invoice" in ui_order else False,
            'to_boleta': ui_order['to_boleta'] if "to_boleta" in ui_order else False,
            'to_ship': ui_order['to_ship'] if "to_ship" in ui_order else False,
            'is_tipped': ui_order.get('is_tipped', False),
            'tip_amount': ui_order.get('tip_amount', 0),
            'access_token': ui_order.get('access_token', '')
        }

    @api.model
    def _process_order(self, order, draft, existing_order):
        res = super(PosOrder, self)._process_order(order, draft, existing_order)
        if order['data']['to_boleta']:
            pos_order = self.env['pos.order'].search([('id', '=', res)])
            pos_order._generate_pos_order_invoice()
            return pos_order.id
        else:
            return res

    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()
        if self.to_boleta and self.state =='paid':
            vals['journal_id'] = self.session_id.config_id.pos_boleta_journal_id.id
            vals['l10n_latam_document_type_id'] = self.env['l10n_latam.document.type'].search(
                [('name', '=', 'Boleta Electrónica')]).id
        return vals

    # @api.model
    # def get_invoice(self, id):
    #     pos_id = self.search([('pos_reference', '=', id)])
    #     base_url = self.env['ir.config_parameter'].get_param('web.base.url')
    #     invoice_id = self.env['account.move'].search(
    #         [('ref', '=', pos_id.name)])
    #     return {
    #         'invoice_name': invoice_id.name,
    #         'document_name': invoice_id.l10n_latam_document_type_id.name,
    #         'barcode': invoice_id.l10n_cl_sii_barcode,
    #     }
