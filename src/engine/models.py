from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import datetime

@dataclass
class UnmatchedTransaction:
    tx_id: str
    source_side: str  # 'SIDE_A_BANK' or 'SIDE_B_LEDGER'
    posting_date: datetime.date
    amount_nok: float
    raw_reference: str
    cleaned_tokens: List[str] = field(default_factory=list)
    matched_group_id: Optional[str] = None
    status: str = "UNRECONCILED"  # 'UNRECONCILED', 'PRE_MATCH_SUGGESTED', 'FINAL_MATCHED'

@dataclass
class VoucherLine:
    account: str
    account_name: str
    debet_nok: float
    kredit_nok: float
    project_id: Optional[str] = None
    wbs_code: Optional[str] = None
    vat_code: str = "0"
    currency: str = "NOK"
    amount_currency: Optional[float] = None

@dataclass
class JournalVoucher:
    voucher_number: str
    posting_date: str
    period: str
    voucher_text: str
    lines: List[VoucherLine]
    voucher_type: str = "SPIN_OFF_CORRECTION"  # 'SPIN_OFF_CORRECTION', 'ACCRUAL_CLOSING', 'AUTO_REVERSAL'
    is_balanced: bool = True
    net_delta_nok: float = 0.0

@dataclass
class PairedVoucherBundle:
    proposal_id: str
    rule_reference: str
    closing_voucher: JournalVoucher
    reversal_voucher: Optional[JournalVoucher] = None
    requires_reversal: bool = True
    status: str = "PENDING_CONTROLLER_APPROVAL"

@dataclass
class AgingBucketSummary:
    bucket_label: str  # '0-30 dager', '31-60 dager', '61-90 dager', '90+ dager'
    total_amount_nok: float
    item_count: int
    items: List[Dict[str, Any]]
    provision_percentage: float
    estimated_loss_nok: float
    audit_risk: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
