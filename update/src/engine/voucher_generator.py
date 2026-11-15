import datetime
import json
from typing import Dict, Any, List, Optional
from src.engine.models import JournalVoucher, VoucherLine, PairedVoucherBundle

class VoucherGenerator:
    """
    Generates balanced, audit-ready Journal Vouchers (Bilag) including:
    1. Spin-off vouchers for bank fees (7770), interest (8150), and agio (8160).
    2. Paired adjusting entries (Bilag A: 31.10) with automatic reversal (Bilag B: 01.11).
    3. Export formatting for ERPs (Visma, Business Central, Xledger, SAP) and SAF-T XML.
    """

    @staticmethod
    def create_spin_off_voucher(
        voucher_number: str,
        posting_date: str,
        transaction_type: str,  # 'BANK_FEE', 'INTEREST', 'CURRENCY_AGIO'
        amount_nok: float,
        bank_account: str = "1920",
        contra_account: Optional[str] = None,
        reference_text: str = "",
        project_id: Optional[str] = None
    ) -> JournalVoucher:
        """
        Creates a balanced spin-off voucher for recurring bank/reconciliation variances.
        """
        if transaction_type == "BANK_FEE":
            expense_acc = contra_account or "7770"
            exp_name = "Bank- og transaksjonsgebyr"
            text = f"Spin-off gebyr: {reference_text}".strip()
            # Bank payout was net, so we record expense (Debit) and clear receivable or adjust bank (Credit)
            lines = [
                VoucherLine(account=expense_acc, account_name=exp_name, debet_nok=amount_nok, kredit_nok=0.0, project_id=project_id),
                VoucherLine(account=bank_account, account_name="Bankinnskudd drift", debet_nok=0.0, kredit_nok=amount_nok, project_id=project_id)
            ]
        elif transaction_type == "INTEREST":
            interest_acc = contra_account or "8150"
            exp_name = "Renter og finansielle rabatter"
            text = f"Spin-off rentepostering: {reference_text}".strip()
            lines = [
                VoucherLine(account=interest_acc, account_name=exp_name, debet_nok=amount_nok, kredit_nok=0.0, project_id=project_id),
                VoucherLine(account=bank_account, account_name="Bankinnskudd drift", debet_nok=0.0, kredit_nok=amount_nok, project_id=project_id)
            ]
        elif transaction_type == "CURRENCY_AGIO":
            agio_acc = contra_account or "8160"
            exp_name = "Valutatap / Agio"
            text = f"Spin-off valutadifferanse (agio): {reference_text}".strip()
            lines = [
                VoucherLine(account=agio_acc, account_name=exp_name, debet_nok=amount_nok, kredit_nok=0.0, project_id=project_id),
                VoucherLine(account="1550", account_name="Mellomregning konsern/valuta", debet_nok=0.0, kredit_nok=amount_nok, project_id=project_id)
            ]
        else:
            raise ValueError(f"Unsupported spin-off transaction type: {transaction_type}")

        total_debet = sum(l.debet_nok for l in lines)
        total_kredit = sum(l.kredit_nok for l in lines)
        delta = round(total_debet - total_kredit, 2)

        return JournalVoucher(
            voucher_number=voucher_number,
            posting_date=posting_date,
            period=posting_date[:7],
            voucher_text=text,
            lines=lines,
            voucher_type="SPIN_OFF_CORRECTION",
            is_balanced=(delta == 0.0),
            net_delta_nok=delta
        )

    @staticmethod
    def create_paired_accrual_bundle(
        proposal_id: str,
        rule_reference: str,
        period_end_date: str,
        voucher_text: str,
        debit_account: str,
        debit_account_name: str,
        credit_account: str,
        credit_account_name: str,
        amount_nok: float,
        project_id: str,
        wbs_code: str,
        requires_reversal: bool = True
    ) -> PairedVoucherBundle:
        """
        Creates Bilag A (closing date) and paired Bilag B (reversal next period).
        """
        close_dt = datetime.datetime.strptime(period_end_date, "%Y-%m-%d").date()
        if close_dt.month == 12:
            reversal_dt = datetime.date(close_dt.year + 1, 1, 1)
        else:
            reversal_dt = datetime.date(close_dt.year, close_dt.month + 1, 1)

        closing_lines = [
            VoucherLine(account=debit_account, account_name=debit_account_name, debet_nok=amount_nok, kredit_nok=0.0, project_id=project_id, wbs_code=wbs_code),
            VoucherLine(account=credit_account, account_name=credit_account_name, debet_nok=0.0, kredit_nok=amount_nok, project_id=project_id, wbs_code=wbs_code)
        ]

        closing_voucher = JournalVoucher(
            voucher_number=f"JV-{close_dt.strftime('%Y%m')}-4412",
            posting_date=period_end_date,
            period=close_dt.strftime('%Y-%m'),
            voucher_text=voucher_text,
            lines=closing_lines,
            voucher_type="ACCRUAL_CLOSING",
            is_balanced=True,
            net_delta_nok=0.0
        )

        reversal_voucher = None
        if requires_reversal:
            reversal_lines = [
                VoucherLine(account=credit_account, account_name=credit_account_name, debet_nok=amount_nok, kredit_nok=0.0, project_id=project_id, wbs_code=wbs_code),
                VoucherLine(account=debit_account, account_name=debit_account_name, debet_nok=0.0, kredit_nok=amount_nok, project_id=project_id, wbs_code=wbs_code)
            ]
            reversal_voucher = JournalVoucher(
                voucher_number=f"JV-{reversal_dt.strftime('%Y%m')}-0001",
                posting_date=reversal_dt.isoformat(),
                period=reversal_dt.strftime('%Y-%m'),
                voucher_text=f"Autoreversering: {voucher_text}",
                lines=reversal_lines,
                voucher_type="AUTO_REVERSAL",
                is_balanced=True,
                net_delta_nok=0.0
            )

        return PairedVoucherBundle(
            proposal_id=proposal_id,
            rule_reference=rule_reference,
            closing_voucher=closing_voucher,
            reversal_voucher=reversal_voucher,
            requires_reversal=requires_reversal
        )

    @staticmethod
    def export_to_saft_xml(vouchers: List[JournalVoucher]) -> str:
        """Generates standard Norwegian SAF-T Financial XML representation."""
        lines_xml = []
        for v in vouchers:
            for idx, l in enumerate(v.lines, start=1):
                lines_xml.append(f"""    <Line>
      <RecordID>{v.voucher_number}-{idx}</RecordID>
      <AccountID>{l.account}</AccountID>
      <Description>{v.voucher_text}</Description>
      <DebitAmount>{l.debet_nok:.2f}</DebitAmount>
      <CreditAmount>{l.kredit_nok:.2f}</CreditAmount>
      <ProjectID>{l.project_id or ''}</ProjectID>
      <WBS>{l.wbs_code or ''}</WBS>
    </Line>""")
        
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<AuditFile xmlns="urn:StandardAuditFile-Taxation-Financial:NO">
  <Header>
    <AuditFileVersion>1.20</AuditFileVersion>
    <CompanyID>981234567MVA</CompanyID>
    <CompanyName>Nordic Engineering Projects AS</CompanyName>
    <TaxAccountingBasis>A</TaxAccountingBasis>
    <CreatedDate>{datetime.date.today().isoformat()}</CreatedDate>
  </Header>
  <GeneralLedgerEntries>
{''.join(lines_xml)}
  </GeneralLedgerEntries>
</AuditFile>"""
        return xml_content

    @staticmethod
    def export_to_erp_csv(vouchers: List[JournalVoucher]) -> str:
        """Generates CSV format ready for Visma.net / Business Central / Xledger."""
        rows = ["VoucherNumber,PostingDate,Period,Account,Debit,Credit,Text,Project,WBS"]
        for v in vouchers:
            for l in v.lines:
                rows.append(f"{v.voucher_number},{v.posting_date},{v.period},{l.account},{l.debet_nok:.2f},{l.kredit_nok:.2f},\"{v.voucher_text}\",{l.project_id or ''},{l.wbs_code or ''}")
        return "\n".join(rows)
