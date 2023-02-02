from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _l10n_cl_edi_post_validation(self):
        if not self._l10n_cl_edi_currency_validation():
            raise UserError(
                _('It is not possible to validate invoices in %s for %s, please convert it to CLP') % (
                    self.currency_id.name, self.l10n_latam_document_type_id.name))
        if (self.l10n_cl_journal_point_of_sale_type == 'online' and
                not ((self.partner_id.l10n_cl_dte_email or self.commercial_partner_id.l10n_cl_dte_email) and
                     self.company_id.l10n_cl_dte_email) and
                not self.l10n_latam_document_type_id._is_doc_type_export() and
                not self.l10n_latam_document_type_id._is_doc_type_ticket()):
            raise UserError(_('The %s %s has not a DTE email defined. This is mandatory for electronic invoicing.') %
                            (_('partner') if not (self.partner_id.l10n_cl_dte_email or
                                                  self.commercial_partner_id.l10n_cl_dte_email) else _('company'), self.partner_id.name))
        if datetime.strptime(self._get_cl_current_strftime(), '%Y-%m-%dT%H:%M:%S').date() < self.invoice_date:
            raise UserError(
                _('The stamp date and time cannot be prior to the invoice issue date and time. TIP: check '
                  'in your user preferences if the timezone is "America/Santiago"'))
        if not self.company_id.l10n_cl_dte_service_provider:
            raise UserError(_(
                'You have not selected an invoicing service provider for your company. '
                'Please go to your company and select one'))
        if not self.company_id.l10n_cl_activity_description:
            raise UserError(_(
                'Your company has not an activity description configured. This is mandatory for electronic '
                'invoicing. Please go to your company and set the correct one (www.sii.cl - Mi SII)'))
        if not self.company_id.l10n_cl_company_activity_ids:
            raise UserError(_(
                'There are no activity codes configured in your company. This is mandatory for electronic '
                'invoicing. Please go to your company and set the correct activity codes (www.sii.cl - Mi SII)'))
        if not self.company_id.l10n_cl_sii_regional_office:
            raise UserError(_(
                'There is no SII Regional Office configured in your company. This is mandatory for electronic '
                'invoicing. Please go to your company and set the regional office, according to your company '
                'address (www.sii.cl - Mi SII)'))
        if (self.l10n_latam_document_type_id.code not in ['39', '41', '110', '111', '112'] and
                not (self.partner_id.l10n_cl_activity_description or
                     self.commercial_partner_id.l10n_cl_activity_description)):
            raise UserError(_(
                'There is not an activity description configured in the '
                'customer %s record. This is mandatory for electronic invoicing for this type of '
                'document. Please go to the partner record and set the activity description') % self.partner_id.name)
        if not self.l10n_latam_document_type_id._is_doc_type_electronic_ticket() and not self.partner_id.street:
            raise UserError(_(
                'There is no address configured in your customer %s record. '
                'This is mandatory for electronic invoicing for this type of document. '
                'Please go to the partner record and set the address') % self.partner_id.name)
        if (self.l10n_latam_document_type_id.code in ['34', '41', '110', '111', '112'] and
                self.amount_untaxed != self.amount_total):
            raise UserError(_('It seems that you are using items with taxes in exempt documents in invoice %s - %s.'
                              ' You must either:\n'
                              '   - Change the document type to a not exempt type.\n'
                              '   - Set an exempt fiscal position to remove taxes automatically.\n'
                              '   - Use products without taxes.\n'
                              '   - Remove taxes from product lines.') % (self.id, self.name))
        if self.l10n_latam_document_type_id.code == '33' and self.amount_untaxed == self.amount_total:
            raise UserError(_('All the items you are billing in invoice %s - %s, have no taxes.\n'
                              ' If you need to bill exempt items you must either use exempt invoice document type (34),'
                              ' or at least one of the items should have vat tax.') % (self.id, self.name))
        if self.l10n_latam_document_type_id.code == '39':
            if self.line_ids.filtered(lambda x: x.tax_group_id.id in [
                self.env.ref('l10n_cl.tax_group_ila').id, self.env.ref('l10n_cl.tax_group_retenciones').id]):
                raise UserError(_('Receipts with withholding taxes are not allowed'))
        self._l10n_cl_edi_validate_boletas()

    def _l10n_cl_edi_validate_boletas(self):
        # Override the method to allow create ticket.
        return None
