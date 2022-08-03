# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api,_
import pdb
import json
from odoo.exceptions import AccessError, UserError, ValidationError


class ContactTypeCus(models.Model):
    _inherit = 'res.partner'

    cash_customers = fields.Boolean("Cash Customer")
    cash_limits = fields.Integer("Cash Limit")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('order_line')
    def cash_limit(self):
        limit = self.env['res.partner'].search([('name', '=', self.partner_id.name)])
        for rec in limit:
            total_amount = json.loads(self.tax_totals_json)['amount_total']
            if total_amount > rec.cash_limits:
                raise ValidationError(_('This customer cash limit is '+str(rec.cash_limits)+' please select the another customer.'))
