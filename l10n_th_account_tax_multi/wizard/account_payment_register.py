# Copyright 2020 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.depends("early_payment_discount_mode")
    def _compute_payment_difference_handling(self):
        res = super()._compute_payment_difference_handling()
        active_ids = self.env.context.get("active_ids", [])
        moves = self.env["account.move"].browse(active_ids)
        wht_move_lines = moves.mapped("line_ids").filtered("wht_tax_id")
        for wizard in self:
            # Auto default reconcile multi when 'Keep Open' only
            if len(wht_move_lines) > 1 and wizard.payment_difference_handling == "open":
                wizard.payment_difference_handling = "reconcile_multi_deduct"
        return res

    @api.onchange("payment_difference_handling")
    def _onchange_payment_difference_handling(self):
        if self.payment_difference_handling != "reconcile_multi_deduct":
            return
        if self.env.context.get("active_model") == "account.move":
            active_ids = self.env.context.get("active_ids", [])
            moves = self.env["account.move"].browse(active_ids)
            move_lines = moves.mapped("line_ids").filtered("wht_tax_id")
            if move_lines:
                # Case WHT only, ensure only 1 wizard
                self.ensure_one()
                (deduction_list, amount_deduct) = move_lines._prepare_deduction_list(
                    self.payment_date, self.currency_id
                )
                deduct_list = []
                for deduct in deduction_list:
                    deduct["analytic_distribution"] = self.deduct_analytic_distribution
                    deduct_list.append(Command.create(deduct))
                self.deduction_ids = [Command.clear()] + deduct_list
                # Set amount only first time
                if float_is_zero(self.payment_difference, precision_digits=2):
                    self.amount -= amount_deduct
                    self._compute_payment_difference()

    def _prepare_deduct_move_line(self, deduct):
        res = super()._prepare_deduct_move_line(deduct)
        res.update(
            {
                "partner_id": deduct.partner_id.id,
                "wht_tax_id": deduct.wht_tax_id.id,
                "tax_base_amount": deduct.wht_amount_base,
            }
        )
        return res


class AccountPaymentDeduction(models.TransientModel):
    _inherit = "account.payment.deduction"

    wht_tax_id = fields.Many2one(
        string="Withholding Tax",
        comodel_name="account.withholding.tax",
        help="Optional hidden field to keep wht_tax. Useful for case 1 tax only",
    )
    wht_amount_base = fields.Monetary(
        string="Withholding Base",
        help="Based amount for the tax amount",
    )
    partner_id = fields.Many2one(comodel_name="res.partner")

    @api.onchange("is_open")
    def _onchange_open(self):
        super()._onchange_open()
        if self.is_open:
            self.wht_tax_id = False
            self.wht_amount_base = False
        return

    @api.onchange("wht_tax_id", "wht_amount_base")
    def _onchange_wht_tax_id(self):
        if self.wht_tax_id and self.wht_amount_base:
            if self.wht_tax_id.is_pit:
                self._onchange_pit()
            else:
                self._onchange_wht()

    def _onchange_wht(self):
        """Onchange set for normal withholding tax"""
        amount_wht = self.wht_tax_id.amount / 100 * self.wht_amount_base
        self.amount = amount_wht
        self.account_id = self.wht_tax_id.account_id
        self.name = self.wht_tax_id.display_name

    def _onchange_pit(self):
        """Onchange set for personal income tax"""
        if not self.wht_tax_id.pit_id:
            raise UserError(
                _("No effective PIT rate for date %s")
                % format_date(self.env, self.payment_id.payment_date)
            )
        payment = self.payment_id
        company = payment.company_id
        amount_base_company = payment.currency_id._convert(
            self.wht_amount_base,
            company.currency_id,
            company,
            payment.payment_date,
        )
        amount_pit_company = self.wht_tax_id.pit_id._compute_expected_wht(
            payment.partner_id,
            amount_base_company,
            pit_date=payment.payment_date,
            currency=company.currency_id,
            company=company,
        )
        amount_pit = company.currency_id._convert(
            amount_pit_company,
            payment.currency_id,
            company,
            payment.payment_date,
        )
        self.amount = amount_pit
        self.account_id = self.wht_tax_id.account_id
        self.name = self.wht_tax_id.display_name
