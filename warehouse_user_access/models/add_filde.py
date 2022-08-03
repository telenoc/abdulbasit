from odoo import api, fields, models


class FieldOnUserAndStock(models.Model):

    _inherit = ["res.users"]

    allowed_warehouse = fields.Many2many('stock.warehouse', 'x_res_users_stock_warehouse_rel', 'res_users_id',
                                         'stock_warehouse_id',
                                         string='Allowed Warehouse',
                                         help="Warehouse assigned to this user")


class FieldOnUserAndStock2(models.Model):

    _inherit = "stock.warehouse"


class FieldOnUserAndStock3(models.Model):

    _inherit = "stock.location"

    linked_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')

class StockQuant(models.Model):

    _inherit = "stock.quant"

    linked_warehouse = fields.Many2one(string='Warehouse', related='location_id.warehouse_id', store=True, index=True)


class FieldOnUserAndStock4(models.Model):

    _inherit = "stock.picking.type"




class FieldOnUserAndStock5(models.Model):

    _inherit = "stock.picking"
