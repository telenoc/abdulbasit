# -*- coding: utf-8 -*-
# from odoo import http


# class PosLedgerReport(http.Controller):
#     @http.route('/pos_ledger_report/pos_ledger_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_ledger_report/pos_ledger_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_ledger_report.listing', {
#             'root': '/pos_ledger_report/pos_ledger_report',
#             'objects': http.request.env['pos_ledger_report.pos_ledger_report'].search([]),
#         })

#     @http.route('/pos_ledger_report/pos_ledger_report/objects/<model("pos_ledger_report.pos_ledger_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_ledger_report.object', {
#             'object': obj
#         })
