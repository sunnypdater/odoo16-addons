# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from dateutil.relativedelta import relativedelta

from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestTaxInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Journal = cls.env["account.journal"]
        # Setup company to allow using tax cash basis
        cls.journal_undue = cls.env["account.journal"].create(
            {"name": "UndueVAT", "type": "general", "code": "UNDUE"}
        )
        cls.company = cls.env.ref("base.main_company")
        cls.company.write(
            {"tax_exigibility": True, "tax_cash_basis_journal_id": cls.journal_undue.id}
        )
        # Journals
        cls.journal_purchase = Journal.search([("type", "=", "purchase")])[0]
        cls.journal_sale = Journal.search([("type", "=", "sale")])[0]
        cls.journal_bank = Journal.search([("type", "=", "bank")])[0]
        # Payment Methods
        cls.payment_method_manual_out = cls.env.ref(
            "account.account_payment_method_manual_out"
        )
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_out"
        )
        # Accounts
        cls.output_vat_acct = cls.env["account.account"].create(
            {"name": "O7", "code": "O7", "account_type": "liability_current"}
        )
        cls.undue_output_vat_acct = cls.env["account.account"].create(
            {"name": "DO7", "code": "DO7", "account_type": "asset_current"}
        )
        cls.input_vat_acct = cls.env["account.account"].create(
            {"name": "V7", "code": "V7", "account_type": "liability_current"}
        )
        cls.input_zero_vat_acct = cls.env["account.account"].create(
            {"name": "V0", "code": "V0", "account_type": "liability_current"}
        )
        cls.undue_input_vat_acct = cls.env["account.account"].create(
            {"name": "DV7", "code": "DV7", "account_type": "asset_current"}
        )
        cls.undue_reconcile_input_vat_acct = cls.env["account.account"].create(
            {
                "name": "DV7 (Reconcile)",
                "code": "DV7rec",
                "account_type": "asset_current",
                "reconcile": True,
            }
        )
        # Tax Group
        cls.tax_group_undue_vat = cls.env["account.tax.group"].create(
            {"name": "UndueVAT"}
        )
        cls.tax_group_vat = cls.env["account.tax.group"].create({"name": "VAT"})
        # Tax
        cls.output_vat = cls.env["account.tax"].create(
            {
                "name": "O7",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 7.0,
                "tax_group_id": cls.tax_group_vat.id,
                "tax_exigibility": "on_invoice",
                "invoice_repartition_line_ids": [
                    Command.create(
                        {"factor_percent": 100.0, "repartition_type": "base"}
                    ),
                    Command.create(
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": cls.output_vat_acct.id,
                        }
                    ),
                ],
            }
        )
        cls.undue_output_vat = cls.env["account.tax"].create(
            {
                "name": "DO7",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": 7.0,
                "tax_group_id": cls.tax_group_undue_vat.id,
                "tax_exigibility": "on_payment",
                "invoice_repartition_line_ids": [
                    Command.create(
                        {"factor_percent": 100.0, "repartition_type": "base"}
                    ),
                    Command.create(
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": cls.output_vat_acct.id,
                        }
                    ),
                ],
                "cash_basis_transition_account_id": cls.undue_output_vat_acct.id,
            }
        )
        cls.input_vat = cls.env["account.tax"].create(
            {
                "name": "V7",
                "type_tax_use": "purchase",
                "amount_type": "percent",
                "amount": 7.0,
                "tax_group_id": cls.tax_group_vat.id,
                "tax_exigibility": "on_invoice",
                "invoice_repartition_line_ids": [
                    Command.create(
                        {"factor_percent": 100.0, "repartition_type": "base"}
                    ),
                    Command.create(
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": cls.input_vat_acct.id,
                        }
                    ),
                ],
            }
        )
        cls.input_zero_vat = cls.env["account.tax"].create(
            {
                "name": "V0",
                "type_tax_use": "purchase",
                "amount_type": "percent",
                "amount": 0.0,
                "tax_group_id": cls.tax_group_vat.id,
                "tax_exigibility": "on_invoice",
                "invoice_repartition_line_ids": [
                    Command.create(
                        {"factor_percent": 100.0, "repartition_type": "base"}
                    ),
                    Command.create(
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": cls.input_zero_vat_acct.id,
                        }
                    ),
                ],
            }
        )
        cls.undue_input_vat = cls.env["account.tax"].create(
            {
                "name": "DV7",
                "type_tax_use": "purchase",
                "amount_type": "percent",
                "amount": 7.0,
                "tax_group_id": cls.tax_group_undue_vat.id,
                "tax_exigibility": "on_payment",
                "invoice_repartition_line_ids": [
                    Command.create(
                        {"factor_percent": 100.0, "repartition_type": "base"}
                    ),
                    Command.create(
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": cls.input_vat_acct.id,
                        }
                    ),
                ],
                "cash_basis_transition_account_id": cls.undue_input_vat_acct.id,
            }
        )
        cls.undue_input_reconcile_vat = cls.env["account.tax"].create(
            {
                "name": "DV7 (reconcile)",
                "type_tax_use": "purchase",
                "amount_type": "percent",
                "amount": 7.0,
                "tax_group_id": cls.tax_group_undue_vat.id,
                "tax_exigibility": "on_payment",
                "invoice_repartition_line_ids": [
                    Command.create(
                        {"factor_percent": 100.0, "repartition_type": "base"}
                    ),
                    Command.create(
                        {
                            "factor_percent": 100.0,
                            "repartition_type": "tax",
                            "account_id": cls.input_vat_acct.id,
                        }
                    ),
                ],
                "cash_basis_transition_account_id": cls.undue_reconcile_input_vat_acct.id,
            }
        )
        cls.payment_term_immediate = cls.env["account.payment.term"].create(
            {"name": "", "line_ids": [Command.create({"value": "balance", "days": 15})]}
        )

        # Optiona tax sequence
        cls.cust_vat_sequence = cls.env["ir.sequence"].create(
            {"name": "Cust VAT Sequence", "padding": 4}
        )

        def create_invoice(name, partner, journal, invoice_type, account_type, vat):
            invoice_dict = {
                "name": name,
                "partner_id": partner.id,
                "journal_id": journal.id,
                "move_type": invoice_type,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    Command.create(
                        {
                            "quantity": 1.0,
                            "account_id": cls.env["account.account"]
                            .search([("account_type", "=", account_type)], limit=1)
                            .id,
                            "name": "Advice",
                            "price_unit": 100.00,
                            "tax_ids": [Command.set([vat.id])],
                        }
                    )
                ],
            }
            return cls.env["account.move"].create(invoice_dict)

        # Prepare Supplier Invoices
        cls.supplier_invoice_vat = create_invoice(
            "Test Supplier Invoice VAT",
            cls.env.ref("base.res_partner_12"),
            cls.journal_purchase,
            "in_invoice",
            "expense",
            cls.input_vat,
        )
        cls.supplier_invoice_undue_vat = create_invoice(
            "Test Supplier Invoice UndueVAT",
            cls.env.ref("base.res_partner_12"),
            cls.journal_purchase,
            "in_invoice",
            "expense",
            cls.undue_input_vat,
        )
        cls.supplier_invoice_undue_vat_partial = create_invoice(
            "Test Supplier Invoice UndueVAT Partial",
            cls.env.ref("base.res_partner_12"),
            cls.journal_purchase,
            "in_invoice",
            "expense",
            cls.undue_input_vat,
        )
        cls.supplier_refund_undue_vat = create_invoice(
            "Test Supplier Refund UndueVAT",
            cls.env.ref("base.res_partner_12"),
            cls.journal_purchase,
            "in_refund",
            "expense",
            cls.undue_input_vat,
        )
        cls.supplier_invoice_undue_vat_reconcile = create_invoice(
            "Test Supplier Invoice UndueVAT (reconcile)",
            cls.env.ref("base.res_partner_12"),
            cls.journal_purchase,
            "in_invoice",
            "expense",
            cls.undue_input_reconcile_vat,
        )
        cls.supplier_invoice_zero_vat = create_invoice(
            "Test Supplier Invoice VAT 0%",
            cls.env.ref("base.res_partner_12"),
            cls.journal_purchase,
            "in_invoice",
            "expense",
            cls.input_zero_vat,
        )

        # Prepare Customer Invoices
        cls.customer_invoice_vat = create_invoice(
            "Test Customer Invoice VAT",
            cls.env.ref("base.res_partner_10"),
            cls.journal_sale,
            "out_invoice",
            "income",
            cls.output_vat,
        )
        cls.customer_invoice_vat_seq = cls.customer_invoice_vat.copy()
        cls.customer_invoice_undue_vat = create_invoice(
            "Test Customer Invoice UndueVAT",
            cls.env.ref("base.res_partner_10"),
            cls.journal_sale,
            "out_invoice",
            "income",
            cls.undue_output_vat,
        )
        cls.customer_invoice_undue_vat_seq = cls.customer_invoice_undue_vat.copy()

    def test_supplier_invoice_vat(self):
        """Supplier Invoice with VAT,
        user must fill in Tax Invoice/Date on Invoice"""
        # User have not filled in Tax Invoice / Date in account_invoice_tax
        with self.assertRaises(UserError) as e:
            self.supplier_invoice_vat.action_post()
        self.assertEqual(e.exception.args[0], "Please fill in tax invoice and tax date")
        tax_invoice = "SINV-10001"
        tax_date = fields.Date.today()
        self.supplier_invoice_vat.tax_invoice_ids.write(
            {"tax_invoice_number": tax_invoice, "tax_invoice_date": tax_date}
        )
        self.supplier_invoice_vat.action_post()
        # Check report late 2 month, report date is not equal tax invoice date
        self.assertEqual(
            self.supplier_invoice_vat.tax_invoice_ids.report_date,
            self.supplier_invoice_vat.tax_invoice_ids.tax_invoice_date,
        )
        with Form(self.supplier_invoice_vat.tax_invoice_ids) as tax:
            tax.report_late_mo = "2"
        move_tax = tax.save()
        self.assertNotEqual(move_tax.report_date, move_tax.tax_invoice_date)

    def test_supplier_invoice_undue_vat(self):
        """Register Payment from Vendor Invoice"""
        # Do not allow user to fill in Tax Invoice/Date
        tax_invoice = "SINV-10001"
        tax_date = fields.Date.today()
        self.supplier_invoice_undue_vat.action_post()
        action = self.supplier_invoice_undue_vat.action_register_payment()
        ctx = action.get("context")
        self.assertFalse(
            self.supplier_invoice_undue_vat.tax_cash_basis_created_move_ids
        )
        # Make full payment from invoice
        with Form(self.env["account.payment.register"].with_context(**ctx)) as f:
            f.journal_id = self.journal_bank
        payment_wiz = f.save()
        res = payment_wiz.action_create_payments()
        payment = self.env["account.payment"].browse(res.get("res_id"))
        self.assertTrue(payment.tax_invoice_ids)
        act_journal_entry = payment.button_open_journal_entry()
        # Check button Journal Entry must have move_id and cash basis
        payment_moves = payment.tax_invoice_move_ids + payment.move_id
        self.assertEqual(act_journal_entry["domain"][0][2], payment_moves.ids)
        # Cash Basis created and state is draft
        bill_tax_cash_basis = (
            self.supplier_invoice_undue_vat.tax_cash_basis_created_move_ids
        )
        self.assertEqual(len(bill_tax_cash_basis), 1)
        self.assertEqual(bill_tax_cash_basis.state, "draft")
        # Test reset payment, tax cash basis in vendor bill must create 1 reversal
        payment.action_draft()
        self.assertEqual(payment.state, "draft")
        # Check button Journal Entry must have only move_id
        act_journal_entry = payment.button_open_journal_entry()
        self.assertEqual(act_journal_entry["res_id"], payment.move_id.id)

        bill_tax_cash_basis = (
            self.supplier_invoice_undue_vat.tax_cash_basis_created_move_ids
        )
        self.assertEqual(len(bill_tax_cash_basis), 2)
        self.assertEqual(list(set(bill_tax_cash_basis.mapped("state"))), ["posted"])
        self.assertFalse(
            any(list(set(bill_tax_cash_basis.line_ids.mapped("reconciled"))))
        )
        # Manual matching, it will create 1 tax cash basis and state is draft
        payment.action_post()
        self.assertEqual(payment.state, "posted")
        payable_account = payment.move_id.partner_id.property_account_payable_id
        ml_payment = payment.move_id.line_ids.filtered(
            lambda l: l.account_id == payable_account
        )
        self.supplier_invoice_undue_vat.js_assign_outstanding_line(ml_payment.id)
        bill_tax_cash_basis = (
            self.supplier_invoice_undue_vat.tax_cash_basis_created_move_ids
        )
        self.assertEqual(len(bill_tax_cash_basis), 3)
        self.assertEqual(
            len(list(set(bill_tax_cash_basis.mapped("state")))), 2
        )  # state draft and posted
        # Clear tax cash basis
        with self.assertRaises(UserError) as e:
            payment.clear_tax_cash_basis()
        self.assertEqual(e.exception.args[0], "Please fill in tax invoice and tax date")
        # Fill in tax invoice and clear undue vat
        payment.tax_invoice_ids.write(
            {"tax_invoice_number": tax_invoice, "tax_invoice_date": tax_date}
        )
        payment.clear_tax_cash_basis()
        # Cash basis journal is now posted
        bill_tax_cash_basis = (
            self.supplier_invoice_undue_vat.tax_cash_basis_created_move_ids
        )
        self.assertEqual(len(bill_tax_cash_basis), 3)
        self.assertEqual(list(set(bill_tax_cash_basis.mapped("state"))), ["posted"])
        # Check the move_line_ids, from both Bank and Cash Basis journal
        self.assertTrue(payment.move_id)
        self.assertTrue(payment.tax_invoice_move_ids)
        payment.action_draft()  # Unlink the relation
        self.assertEqual(payment.move_id.state, "draft")
        self.assertFalse(payment.tax_invoice_move_ids)

    def test_supplier_invoice_undue_vat_reconcile(self):
        """Register Payment from Vendor Invoice"""
        # Do not allow user to fill in Tax Invoice/Date
        tax_invoice = "SINV-10001"
        tax_date = fields.Date.today()
        self.supplier_invoice_undue_vat_reconcile.action_post()
        action = self.supplier_invoice_undue_vat_reconcile.action_register_payment()
        ctx = action.get("context")
        self.assertFalse(
            self.supplier_invoice_undue_vat_reconcile.tax_cash_basis_created_move_ids
        )
        # Make full payment from invoice
        with Form(self.env["account.payment.register"].with_context(**ctx)) as f:
            f.journal_id = self.journal_bank
        payment_wiz = f.save()
        res = payment_wiz.action_create_payments()
        payment = self.env["account.payment"].browse(res.get("res_id"))
        self.assertTrue(payment.tax_invoice_ids)
        # Cash Basis created and state is draft
        bill_tax_cash_basis = (
            self.supplier_invoice_undue_vat_reconcile.tax_cash_basis_created_move_ids
        )
        self.assertEqual(len(bill_tax_cash_basis), 1)
        self.assertEqual(bill_tax_cash_basis.state, "draft")
        # Test reset payment, tax cash basis in vendor bill must create 1 reversal
        # and reconciled
        payment.action_draft()
        self.assertEqual(payment.state, "draft")

        bill_tax_cash_basis = (
            self.supplier_invoice_undue_vat_reconcile.tax_cash_basis_created_move_ids
        )
        self.assertEqual(len(bill_tax_cash_basis), 2)
        self.assertEqual(list(set(bill_tax_cash_basis.mapped("state"))), ["posted"])
        self.assertTrue(
            any(list(set(bill_tax_cash_basis.line_ids.mapped("reconciled"))))
        )
        # Manual matching, it will create 1 tax cash basis and state is draft
        payment.action_post()
        self.assertEqual(payment.state, "posted")
        payable_account = payment.move_id.partner_id.property_account_payable_id
        ml_payment = payment.move_id.line_ids.filtered(
            lambda l: l.account_id == payable_account
        )
        self.supplier_invoice_undue_vat_reconcile.js_assign_outstanding_line(
            ml_payment.id
        )
        bill_tax_cash_basis = (
            self.supplier_invoice_undue_vat_reconcile.tax_cash_basis_created_move_ids
        )
        self.assertEqual(len(bill_tax_cash_basis), 3)
        self.assertEqual(
            len(list(set(bill_tax_cash_basis.mapped("state")))), 2
        )  # state draft and posted
        # Clear tax cash basis
        with self.assertRaises(UserError) as e:
            payment.clear_tax_cash_basis()
        self.assertEqual(e.exception.args[0], "Please fill in tax invoice and tax date")
        # Fill in tax invoice and clear undue vat
        payment.tax_invoice_ids.write(
            {"tax_invoice_number": tax_invoice, "tax_invoice_date": tax_date}
        )
        payment.clear_tax_cash_basis()
        # Cash basis journal is now posted
        bill_tax_cash_basis = (
            self.supplier_invoice_undue_vat_reconcile.tax_cash_basis_created_move_ids
        )
        self.assertEqual(len(bill_tax_cash_basis), 3)
        self.assertEqual(list(set(bill_tax_cash_basis.mapped("state"))), ["posted"])
        # Check the move_line_ids, from both Bank and Cash Basis journal
        self.assertTrue(payment.move_id)
        self.assertTrue(payment.tax_invoice_move_ids)
        payment.action_draft()  # Unlink the relation
        self.assertEqual(payment.move_id.state, "draft")
        self.assertFalse(payment.tax_invoice_move_ids)

    def test_supplier_invoice_undue_vat_partial_payment(self):
        """Register Partial Payment from Vendor Invoice"""
        # Do not allow user to fill in Tax Invoice/Date
        fields.Date.today()
        self.supplier_invoice_undue_vat_partial.action_post()
        action = self.supplier_invoice_undue_vat_partial.action_register_payment()
        ctx = action.get("context")

        # Make full payment from invoice
        with Form(self.env["account.payment.register"].with_context(**ctx)) as f:
            f.journal_id = self.journal_bank
            f.amount = 30
            f.payment_difference_handling = "open"
        payment_wiz = f.save()
        res = payment_wiz.action_create_payments()
        payment = self.env["account.payment"].browse(res.get("res_id"))
        self.assertTrue(payment.tax_invoice_ids)
        self.assertEqual(payment.amount, 30.00)
        self.assertEqual(payment.reconciled_bill_ids.payment_state, "partial")
        self.assertEqual(payment.reconciled_bill_ids.amount_residual, 77)
        tax_calculated = 1.96  # payment - (payment * 100)/107
        # NOTE: tax base amount is not correct because tax_calculated round 2 digits
        tax_base_cal = (tax_calculated * 100) / 7  # calculat base tax
        self.assertEqual(payment.tax_invoice_ids.balance, tax_calculated)
        self.assertEqual(payment.tax_invoice_ids.tax_base_amount, tax_base_cal)
        # Not allow delete tax invoice if it has 1 line.
        with self.assertRaises(UserError):
            payment.tax_invoice_ids.unlink()
        self.assertEqual(len(payment.tax_invoice_ids), 1)
        payment.tax_invoice_ids.with_context(force_remove_tax_invoice=1).unlink()
        self.assertEqual(len(payment.tax_invoice_ids), 0)

    def test_customer_invoice_vat(self):
        """Customer Invoice with VAT,
        system auto fill in Tax Invoice/Date on Invoice"""
        self.customer_invoice_vat.action_post()
        tax_invoices = self.customer_invoice_vat.tax_invoice_ids
        tax_invoice_number = tax_invoices.mapped("tax_invoice_number")[0]
        self.assertEqual(tax_invoice_number, "Test Customer Invoice VAT")

    def test_customer_invoice_undue_vat(self):
        """Register Payment from Customer Invoice"""
        # Do not allow user to fill in Tax Invoice/Date
        self.customer_invoice_undue_vat.action_post()
        action = self.customer_invoice_undue_vat.action_register_payment()
        ctx = action.get("context")
        # Make full payment from invoice
        with Form(self.env["account.payment.register"].with_context(**ctx)) as f:
            f.journal_id = self.journal_bank
        payment_wiz = f.save()
        res = payment_wiz.action_create_payments()
        payment = self.env["account.payment"].browse(res.get("res_id"))
        self.assertTrue(payment.tax_invoice_ids)
        # Clear tax cash basis
        payment.clear_tax_cash_basis()
        # Cash basis journal is now posted
        tax_invoices = payment.tax_invoice_ids
        self.assertEqual(tax_invoices.mapped("move_id").state, "posted")
        tax_invoice_number = tax_invoices.mapped("tax_invoice_number")[0]
        self.assertEqual(tax_invoice_number, payment.name)
        # Check the move_line_ids, from both Bank and Cash Basis journal
        self.assertTrue(payment.move_id)
        self.assertTrue(payment.tax_invoice_move_ids)
        payment.action_draft()  # Unlink the relation
        self.assertEqual(payment.move_id.state, "draft")
        self.assertFalse(payment.tax_invoice_move_ids)

    def test_customer_invoice_vat_sequence(self):
        """Customer Invoice with VAT,
        system auto fill in Tax Invoice using sequence"""
        self.assertEqual(
            self.customer_invoice_vat_seq.company_id.customer_tax_invoice_number,
            "payment",
        )
        cust_inv_vat_doc = self.customer_invoice_vat_seq.copy()
        cust_inv_vat_doc.action_post()
        tax_invoices = cust_inv_vat_doc.tax_invoice_ids
        tax_invoice_number = tax_invoices.mapped("tax_invoice_number")[0]
        # tax invoice number will auto fill following payment
        # This is not undue vat, so document there is value same as invoice
        self.assertEqual(tax_invoice_number, cust_inv_vat_doc.name)

        # Set customer tax invoice number = 'invoice'
        self.company.customer_tax_invoice_number = "invoice"
        self.assertEqual(
            self.customer_invoice_vat_seq.company_id.customer_tax_invoice_number,
            "invoice",
        )
        cust_inv_vat_doc_sequence_inv = self.customer_invoice_vat_seq.copy()
        cust_inv_vat_doc_sequence_inv.action_post()
        tax_invoices = cust_inv_vat_doc_sequence_inv.tax_invoice_ids
        tax_invoice_number = tax_invoices.mapped("tax_invoice_number")[0]
        # tax invoice number will auto fill following invoice
        self.assertEqual(tax_invoice_number, cust_inv_vat_doc_sequence_inv.name)

        # Assign opptional sequence to vat
        self.cust_vat_sequence.prefix = "CTX"
        self.cust_vat_sequence.number_next_actual = 1  # CTX0001
        self.output_vat.taxinv_sequence_id = self.cust_vat_sequence
        self.customer_invoice_vat_seq.action_post()
        tax_invoices = self.customer_invoice_vat_seq.tax_invoice_ids
        tax_invoice_number = tax_invoices.mapped("tax_invoice_number")[0]
        self.assertEqual(tax_invoice_number, "CTX0001")

    def test_customer_invoice_undue_vat_sequence(self):
        """Register Payment from Customer Invoice
        system auto fill in Tax Invoice using sequence"""
        self.assertEqual(
            self.customer_invoice_undue_vat_seq.company_id.customer_tax_invoice_number,
            "payment",
        )
        cust_undue_doc = self.customer_invoice_undue_vat_seq.copy()
        cust_undue_doc.action_post()
        # Make full payment from invoice
        action = cust_undue_doc.action_register_payment()
        ctx = action.get("context")
        with Form(self.env["account.payment.register"].with_context(**ctx)) as f:
            f.journal_id = self.journal_bank
        payment_wiz = f.save()
        res = payment_wiz.action_create_payments()
        payment = self.env["account.payment"].browse(res.get("res_id"))
        self.assertTrue(payment.tax_invoice_ids)
        tax_invoices = payment.tax_invoice_ids
        tax_invoice_number = tax_invoices.mapped("tax_invoice_number")[0]
        self.assertEqual(tax_invoice_number, payment.name)

        # Set customer tax invoice number = 'invoice'
        self.company.customer_tax_invoice_number = "invoice"
        self.assertEqual(
            self.customer_invoice_undue_vat_seq.company_id.customer_tax_invoice_number,
            "invoice",
        )
        cust_undue_doc_seq_invoice = self.customer_invoice_undue_vat_seq.copy()
        cust_undue_doc_seq_invoice.action_post()
        # Make full payment from invoice
        action = cust_undue_doc_seq_invoice.action_register_payment()
        ctx = action.get("context")
        with Form(self.env["account.payment.register"].with_context(**ctx)) as f:
            f.journal_id = self.journal_bank
        payment_wiz = f.save()
        res = payment_wiz.action_create_payments()
        payment = self.env["account.payment"].browse(res.get("res_id"))
        self.assertTrue(payment.tax_invoice_ids)
        tax_invoices = payment.tax_invoice_ids
        tax_invoice_number = tax_invoices.mapped("tax_invoice_number")[0]
        self.assertEqual(tax_invoice_number, cust_undue_doc_seq_invoice.name)

        # Assign opptional sequence to undue vat
        self.cust_vat_sequence.prefix = "CTX"
        self.cust_vat_sequence.number_next_actual = 2  # CTX0002
        self.undue_output_vat.taxinv_sequence_id = self.cust_vat_sequence
        self.assertEqual(self.undue_output_vat.sequence_number_next, 2)
        self.undue_output_vat.sequence_number_next = 5  # Change sequence number to 5
        # Do not allow user to fill in Tax Invoice/Date
        self.customer_invoice_undue_vat_seq.action_post()
        # Make full payment from invoice
        action = self.customer_invoice_undue_vat_seq.action_register_payment()
        ctx = action.get("context")
        with Form(self.env["account.payment.register"].with_context(**ctx)) as f:
            f.journal_id = self.journal_bank
        payment_wiz = f.save()
        res = payment_wiz.action_create_payments()
        payment = self.env["account.payment"].browse(res.get("res_id"))
        self.assertTrue(payment.tax_invoice_ids)
        # Clear tax cash basis
        payment.clear_tax_cash_basis()
        # Cash basis journal is now posted
        tax_invoices = payment.tax_invoice_ids
        self.assertEqual(tax_invoices.mapped("move_id").state, "posted")
        tax_invoice_number = tax_invoices.mapped("tax_invoice_number")[0]
        self.assertEqual(tax_invoice_number, "CTX0005")
        # Check the move_line_ids, from both Bank and Cash Basis journal
        self.assertTrue(payment.move_id)
        self.assertTrue(payment.tax_invoice_move_ids)
        payment.action_draft()  # Unlink the relation
        self.assertEqual(payment.move_id.state, "draft")
        self.assertFalse(payment.tax_invoice_move_ids)

    def test_supplier_invoice_refund_reconcile(self):
        """Case on undue vat, to net refund with vendor bill.
        In this case, cash basis journal entry will be created, make sure it
        can not post until all Tax Invoice number is filled"""
        # Post suupplier invoice
        invoice = self.supplier_invoice_undue_vat.copy()
        invoice.invoice_date = invoice.date
        invoice.action_post()
        # Post supplier refund
        refund = self.supplier_refund_undue_vat.copy()
        refund.invoice_date = refund.date
        refund.action_post()
        # At invoice add refund to reconcile
        payable_account = refund.partner_id.property_account_payable_id
        refund_ml = refund.line_ids.filtered(lambda l: l.account_id == payable_account)
        invoice.js_assign_outstanding_line(refund_ml.id)
        cash_basis_entries = self.env["account.move"].search(
            [("ref", "in", [invoice.name, refund.name])]
        )
        for move in cash_basis_entries:
            with self.assertRaises(UserError):
                move.action_post()

    def test_supplier_invoice_reversal(self):
        """Case on reversal vendor bill."""
        # Post suupplier invoice
        tax_invoice = "SINV-10001"
        tax_date = fields.Date.today()
        self.supplier_invoice_vat.tax_invoice_ids.write(
            {"tax_invoice_number": tax_invoice, "tax_invoice_date": tax_date}
        )
        self.supplier_invoice_vat.action_post()
        # Add credit note
        ctx = {
            "active_ids": self.supplier_invoice_vat.ids,
            "active_model": "account.move",
        }
        with Form(self.env["account.move.reversal"].with_context(**ctx)) as f:
            f.refund_method = "cancel"
        reversal_move = f.save()
        # Can't reversal move, if not add tax number, date in account.move.reversal
        with self.assertRaises(UserError):
            reversal_move.reverse_moves()
        tax_reversal_invoice = "RSINV-10001"
        reversal_move.write(
            {"tax_invoice_number": tax_reversal_invoice, "tax_invoice_date": tax_date}
        )
        reversal_move.reverse_moves()
        self.assertEqual(self.supplier_invoice_vat.payment_state, "reversed")

    def test_included_tax(self):
        """
        Test an account.move.line is created automatically when adding a tax.
        This test uses the following scenario:
            - Create manually a debit line of 1000 having an included tax.
            - Assume a line containing the tax amount is created automatically.
            - Create manually a credit line to balance the two previous lines.
            - Save the move.

        included tax = 20%

        Name                   | Debit     | Credit    | Tax_ids       | Tax_line_id's name
        -----------------------|-----------|-----------|---------------|-------------------
        debit_line_1           | 1000      |           | tax           |
        included_tax_line      | 200       |           |               | included_tax_line
        credit_line_1          |           | 1200      |               |
        """

        self.included_percent_tax = self.env["account.tax"].create(
            {
                "name": "included_tax_line",
                "amount_type": "percent",
                "amount": 20,
                "price_include": True,
                "include_base_amount": False,
            }
        )

        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit_line_1",
                            "account_id": self.input_vat_acct.id,
                            "tax_ids": [Command.set(self.included_percent_tax.ids)],
                            "balance": 1000.0,  # debit
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit_line_1",
                            "account_id": self.input_vat_acct.id,
                            "balance": -1200.0,  # credit
                        },
                    ),
                ],
            }
        )
        self.assertRecordValues(
            move.line_ids,
            [
                {
                    "name": "debit_line_1",
                    "debit": 1000.0,
                    "credit": 0.0,
                    "tax_ids": [self.included_percent_tax.id],
                    "tax_line_id": False,
                },
                {
                    "name": "credit_line_1",
                    "debit": 0.0,
                    "credit": 1200.0,
                    "tax_ids": [],
                    "tax_line_id": False,
                },
                {
                    "name": "included_tax_line",
                    "debit": 200.0,
                    "credit": 0.0,
                    "tax_ids": [],
                    "tax_line_id": self.included_percent_tax.id,
                },
            ],
        )

    def test_supplier_invoice_zero_tax(self):
        """Case on 0% tax, Core odoo not create line with zero tax"""
        invoice = self.supplier_invoice_zero_vat
        line_zero = invoice.line_ids.filtered(lambda l: not (l.debit or l.credit))
        # There is 1 line for tax 0%
        self.assertEqual(len(invoice.line_ids), 3)
        self.assertTrue(line_zero)
        self.assertEqual(len(line_zero), 1)

    def test_journal_entry_manual_tax(self):
        """Case manual tax in journal entry"""
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit_line_1",
                            "account_id": self.input_vat_acct.id,
                            "balance": 1000.0,  # debit
                        }
                    ),
                    Command.create(
                        {
                            "name": "tax_line_1",
                            "account_id": self.input_vat_acct.id,
                            "balance": 200.0,  # debit
                        },
                    ),
                    Command.create(
                        {
                            "name": "credit_line_1",
                            "account_id": self.input_vat_acct.id,
                            "balance": -1200.0,  # credit
                        },
                    ),
                ],
            }
        )
        self.assertFalse(move.tax_invoice_ids)
        # Add tax manual in line tax
        line_tax = move.line_ids.filtered(lambda l: l.balance == 200.0)
        line_tax.manual_tax_invoice = True
        self.assertTrue(move.tax_invoice_ids)
        self.assertEqual(move.tax_invoice_ids.tax_base_amount, 0.0)
        self.assertEqual(move.tax_invoice_ids.balance, 200.0)
        today = fields.Date.today()
        move.tax_invoice_ids.tax_invoice_number = "TEST_TAX001"
        move.tax_invoice_ids.tax_invoice_date = today
        # Check tax report late 2 months
        previous_2_month = today - relativedelta(months=2)
        with Form(move.tax_invoice_ids) as tax_inv:
            tax_inv.tax_invoice_date = previous_2_month
        tax_inv.save()
        self.assertEqual(move.tax_invoice_ids.report_late_mo, "2")
        # Check tax report late > 6 months
        previous_10_month = today - relativedelta(months=10)
        with Form(move.tax_invoice_ids) as tax_inv:
            tax_inv.tax_invoice_date = previous_10_month
        tax_inv.save()
        self.assertEqual(move.tax_invoice_ids.report_late_mo, "0")
        # Check tax report late 0 month
        with Form(move.tax_invoice_ids) as tax_inv:
            tax_inv.tax_invoice_date = today
        tax_inv.save()
        self.assertEqual(move.tax_invoice_ids.report_late_mo, "0")
        line_tax.manual_tax_invoice = False
        self.assertFalse(move.tax_invoice_ids)
