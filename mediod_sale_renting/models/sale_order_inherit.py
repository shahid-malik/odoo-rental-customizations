# -*- coding: utf-8 -*-
import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_damage = fields.Boolean('Damage')
    rental_forecast_qty = fields.Float(compute='_compute_rental_forecast_qty')
    rental_order_qty = fields.Float(compute='_compute_rental_order_qty')

    # def action_confirm(self):
    #     for rec in self.order_line:
    #         if rec.product_template_id.with_context({'to_date': self.rental_start_date}).qty_available - rec.product_template_id.rental_forecast_qty < 0 or rec.product_uom_qty > rec.product_template_id.qty_available:
    #             raise ValidationError("%s is not available in stock" % rec.product_template_id.name)
    #     return super().action_confirm()

    # product.with_context({'to_date': date_val}).qty_available

    def _compute_rental_forecast_qty(self):
        for rec in self:
            rec.rental_forecast_qty = 0.0
            for res in rec.order_line:
                res.product_id.rental_forecast_qty = 0.0
                product_in_so_lines = self.env['sale.order.line'].search(
                    [('product_id', '=', res.product_id.id), ('is_rental', '=', True)])
                if product_in_so_lines:
                    confirm_so_lines = product_in_so_lines.filtered(lambda x: x.order_id.state in ('draft', 'sent'))
                    quantity = 0.0
                    for record in confirm_so_lines:
                        quantity += record.product_uom_qty
                    res.product_id.rental_forecast_qty = quantity
                    rec.rental_forecast_qty = quantity
                    print('name', res.product_id.name, 'quantity', res.product_id.rental_forecast_qty)

    def _compute_rental_order_qty(self):
        for rec in self:
            rec.rental_order_qty = 0.0
            for res in rec.order_line:
                product_in_so_lines = self.env['sale.order.line'].search(
                    [('product_id', '=', res.product_id.id), ('is_rental', '=', True)])
                if product_in_so_lines:
                    confirm_so_lines = product_in_so_lines.filtered(
                        lambda x: x.order_id.rental_status in ('pickup', 'draft'))
                    print('len', len(confirm_so_lines))
                    quantity = 0.0
                    for record in confirm_so_lines:
                        quantity += record.product_uom_qty
                    res.product_id.rental_order_qty = quantity
                    rec.rental_order_qty = quantity
                    print('name', res.product_id.name, 'quantity_order_rental', res.product_id.rental_order_qty,
                          'sale_order', res.order_id.name)

                print(res)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.is_rental_order == True:
            for rec in res.order_line:
                print(rec.product_template_id.with_context({'to_date': res.rental_return_date}).qty_available)
                print(rec.virtual_available_at_date)
                if rec.product_template_id.with_context({
                                                            'to_date': res.rental_return_date}).qty_available - rec.product_template_id.rental_order_qty <= 0 or rec.product_uom_qty > rec.product_template_id.qty_available:
                    raise ValidationError("%s is not available in stock" % rec.product_template_id.name)
                    # for quant in rec.product_id.stock_quant_ids:
                    # if quant.available_quantity == 0 or rec.product_uom_qty > quant.available_quantity:
                    #     raise ValidationError("%s is not available in stock" % rec.product_template_id.name)

                # if rec.product_template_id.qty_available == 0 or rec.product_uom_qty > rec.product_template_id.qty_available:
                #     raise ValidationError("%s is not available in stock" % rec.product_template_id.name)
        # if res.is_rental_order == True:
        #     for rec in res.order_line:
        #         if rec.product_template_id.qty_available - rec.product_template_id.rental_forecast_qty <= 0 or rec.product_uom_qty > rec.product_template_id.qty_available:
        #             raise ValidationError("%s is not available in stock" % rec.product_template_id.name)
        #             # for quant in rec.product_id.stock_quant_ids:
        #             # if quant.available_quantity == 0 or rec.product_uom_qty > quant.available_quantity:
        #             #     raise ValidationError("%s is not available in stock" % rec.product_template_id.name)
        #
        #         # if rec.product_template_id.qty_available == 0 or rec.product_uom_qty > rec.product_template_id.qty_available:
        #         #     raise ValidationError("%s is not available in stock" % rec.product_template_id.name)

        return res

    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if self.is_rental_order == True:
            for rec in self.order_line:
                print(rec.product_template_id.with_context({'to_date': self.rental_start_date}).qty_available)
                if rec.product_template_id.with_context({
                    'to_date': self.rental_start_date}).qty_available - rec.product_template_id.rental_order_qty <= 0 or rec.product_uom_qty > rec.product_template_id.qty_available:
                    raise ValidationError("%s is not available in stock" % rec.product_template_id.name)
            for rec in self.order_line:
                if rec.product_template_id.qty_available - rec.product_template_id.rental_forecast_qty < 0 or rec.product_uom_qty > rec.product_template_id.qty_available:
                    raise ValidationError("%s is not available in stock" % rec.product_template_id.name)
                # if rec.product_template_id.qty_available == 0 or rec.product_uom_qty > rec.product_template_id.qty_available:
                #     raise ValidationError("%s is not available in stock" % rec.product_template_id.name)

        return result

    @api.onchange('is_damage')
    def send_damage_mail(self):
        for rec in self:
            if rec.is_damage == True:
                template_id = self.env.ref('mediod_sale_renting.notification_emial_template')
                if template_id:
                    # order_line_partners = self.mapped('order_partner_id')
                    template_id.email_to = rec.user_id.email
                    template_id.send_mail(rec.id, force_send=True)


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    rental_forecast_qty = fields.Float('Rental Reserve Quantity')
    rental_order_qty = fields.Float('Rental Order Quantity')
#
#     @api.onchange('product_template_id')
#     def _compute_rental_forecast_qty(self):
#         for rec in self:
#             print('aqib')
#             rec.rental_forecast_qty = 0.0
#             product_in_so_lines = self.env['sale.order.line'].search([('product_id','=',rec.id),('is_rental','=',True)])
#             if product_in_so_lines:
#                 confirm_so_lines = product_in_so_lines.filtered(lambda x:x.order_id.state == 'sale')
#                 quantity = 0.0
#                 for res in confirm_so_lines:
#                     quantity += res.product_uom_qty
#                 rec.rental_forecast_qty = rec.qty_available - quantity
#                 print(rec.rental_forecast_qty)
