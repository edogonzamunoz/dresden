from odoo import fields, models, api
from functools import partial

class PosOrder(models.Model):
    _inherit = 'pos.order'

    to_boleta = fields.Boolean('To boleta', copy=False)

    @api.depends("account_move")
    def _compute_l10n_cl_sii_barcode(self):
        for order in self:
            order.update({
                    'l10n_cl_sii_barcode': order.account_move.l10n_cl_sii_barcode,
                })

    l10n_cl_sii_barcode = fields.Char(compute="_compute_l10n_cl_sii_barcode")

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


    def get_invoice_info(self):
        l10n_latam_document_name = self.account_move.l10n_latam_document_type_id.name
        l10n_latam_document_code = self.account_move.l10n_latam_document_type_id.code
        l10n_latam_document_number = self.account_move.l10n_latam_document_number
        invoice_barcode_stamp = ""
        if self.account_move:
            invoice_barcode_stamp = self.account_move._pdf417_barcode(self.account_move.l10n_cl_sii_barcode)

        return {
            'l10n_latam_document_name':l10n_latam_document_name,
            'l10n_latam_document_code':l10n_latam_document_code,
            'l10n_latam_document_number':l10n_latam_document_number,
            'invoice_barcode_stamp':invoice_barcode_stamp,
            'journal_id':self.account_move.journal_id.name,
        }

    @api.model
    def create_from_ui(self, orders, draft=False):
        """ Create and update Orders from the frontend PoS application.

        Create new orders and update orders that are in draft status. If an order already exists with a status
        diferent from 'draft'it will be discareded, otherwise it will be saved to the database. If saved with
        'draft' status the order can be overwritten later by this function.

        :param orders: dictionary with the orders to be created.
        :type orders: dict.
        :param draft: Indicate if the orders are ment to be finalised or temporarily saved.
        :type draft: bool.
        :Returns: list -- list of db-ids for the created and updated orders.
        """
        order_ids = []
        for order in orders:
            existing_order = False
            if 'server_id' in order['data']:
                existing_order = self.env['pos.order'].search(['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])], limit=1)
            if (existing_order and existing_order.state == 'draft') or not existing_order:
                order_ids.append(self._process_order(order, draft, existing_order))

        res = self.env['pos.order'].search_read(domain=[('id', 'in', order_ids)], fields=['id', 'pos_reference', 'account_move'], load=False)
        for data in res:
            order_data = self.browse(data['id']).get_invoice_info()
            data.update(order_data)

        return res


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'


    def generate_wrapped_product_name(self):
        MAX_LENGTH = 24 # 40 * line ratio of .6
        wrapped = []
        name = self.product_id.name
        current_line = ""

        while len(name) > 0:
            space_index = name.find(" ")

            if space_index == -1:
                space_index = len(name)

            if len(current_line) + space_index > MAX_LENGTH:
                if len(current_line):
                    wrapped.append(current_line)
                current_line = ""

            current_line += name[:space_index + 1]
            name = name[space_index + 1:]
        
        if len(current_line):
            wrapped.append(current_line)

        if wrapped:
            return wrapped[0]
        else:   
            return ""


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
