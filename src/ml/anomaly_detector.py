"""
CLOSE-AI: Multivariate Statistical Anomaly Detection Pipeline (Isolation Forest)
Implements Section 5 of system specification:
- 11-dimensional engineered feature matrix
- Scikit-learn IsolationForest with StandardScaler
- Anomaly scoring normalized [0, 100]
- Explainable feature contribution attribution
"""

import os
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class CloseAnomalyDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=100,
            max_samples="auto",
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=1
        )
        self.is_fitted = False

    def _benford_score(self, val: float) -> float:
        """
        Calculates deviation of leading digit from Benford's Law expected probability.
        P(d) = log10(1 + 1/d)
        """
        try:
            val_abs = abs(val)
            if val_abs < 1.0:
                return 0.0
            first_digit = int(str(int(val_abs))[0])
            if first_digit < 1 or first_digit > 9:
                return 0.0
            benford_expected = math.log10(1 + 1 / first_digit)
            # High risk if first digit deviates substantially from Benford expected (e.g. 9s or 4s)
            return float(abs(1.0 / first_digit - benford_expected))
        except Exception:
            return 0.0

    def extract_features(self, df_gl: pd.DataFrame, df_invoices: pd.DataFrame = None) -> pd.DataFrame:
        """
        Builds the 11-dimensional feature matrix for general ledger lines and invoices.
        """
        df = df_gl.copy()

        # Target amount (use debit if > 0 else credit)
        df["amount_nok"] = np.where(df["debit_nok"] > 0, df["debit_nok"], df["credit_nok"])
        df["amount_nok"] = df["amount_nok"].astype(float)

        # 1. amount_log_scaled
        df["amount_log_scaled"] = np.log1p(df["amount_nok"].clip(lower=0))

        # 2. amount_zscore_by_account
        acct_stats = df.groupby("account_number")["amount_nok"].agg(["mean", "std"]).reset_index()
        acct_stats["std"] = acct_stats["std"].replace(0, 1.0).fillna(1.0)
        df = df.merge(acct_stats, on="account_number", how="left")
        df["amount_zscore_by_account"] = ((df["amount_nok"] - df["mean"]) / df["std"]).fillna(0.0).clip(-5, 5)
        df = df.drop(columns=["mean", "std"])

        # 3. amount_zscore_by_cc
        cc_stats = df.groupby("cost_center")["amount_nok"].agg(["mean", "std"]).reset_index()
        cc_stats["std"] = cc_stats["std"].replace(0, 1.0).fillna(1.0)
        df = df.merge(cc_stats, on="cost_center", how="left")
        df["amount_zscore_by_cc"] = ((df["amount_nok"] - df["mean"]) / df["std"]).fillna(0.0).clip(-5, 5)
        df = df.drop(columns=["mean", "std"])

        # Dates & temporal features
        if "posting_date" in df.columns:
            dates = pd.to_datetime(df["posting_date"])
        else:
            dates = pd.to_datetime("2026-10-25")

        # 4. is_weekend
        df["is_weekend"] = dates.dt.dayofweek.isin([5, 6]).astype(int)

        # 5 & 6. posting_hour_sin, posting_hour_cos (simulated: manual off-hours at 22:00, automated at 10:00)
        hours = np.where(
            df.get("created_by", "").str.contains("temp|manual|junior", case=False, na=False),
            22.0, 10.0
        )
        df["posting_hour_sin"] = np.sin(2 * np.pi * hours / 24.0)
        df["posting_hour_cos"] = np.cos(2 * np.pi * hours / 24.0)

        # 7. days_to_period_end (October has 31 days)
        df["days_to_period_end"] = (31 - dates.dt.day).clip(lower=0)

        # 8. vendor_frequency_score (frequency of project activity)
        prj_counts = df["project_id"].value_counts(normalize=True).to_dict()
        df["vendor_frequency_score"] = df["project_id"].map(prj_counts).fillna(0.05)

        # 9. benford_first_digit_risk
        df["benford_first_digit_risk"] = df["amount_nok"].apply(self._benford_score)

        # 10. is_round_thousand
        df["is_round_thousand"] = ((df["amount_nok"] % 1000 == 0) & (df["amount_nok"] > 10000)).astype(int)

        # 11. missing_dimension_flag
        df["missing_dimension_flag"] = (
            (df["account_number"].astype(str).str.startswith("4")) & 
            (df["project_id"].isna() | df["wbs_code"].isna())
        ).astype(int)

        feature_cols = [
            "amount_log_scaled",
            "amount_zscore_by_account",
            "amount_zscore_by_cc",
            "is_weekend",
            "posting_hour_sin",
            "posting_hour_cos",
            "days_to_period_end",
            "vendor_frequency_score",
            "benford_first_digit_risk",
            "is_round_thousand",
            "missing_dimension_flag"
        ]

        return df, feature_cols

    def fit_predict(self, df_gl: pd.DataFrame) -> pd.DataFrame:
        """
        Fits Isolation Forest and predicts anomaly scores for each line item.
        """
        df_enriched, feature_cols = self.extract_features(df_gl)
        X = df_enriched[feature_cols].values
        
        # Scale
        X_scaled = self.scaler.fit_transform(X)
        self.is_fitted = True

        # Fit Isolation Forest
        self.model.fit(X_scaled)
        predictions = self.model.predict(X_scaled)  # -1 for anomaly, 1 for inlier
        raw_scores = self.model.decision_function(X_scaled)

        # Normalize score to [0, 100] where 100 is most anomalous
        score_min, score_max = raw_scores.min(), raw_scores.max()
        if score_max > score_min:
            norm_scores = (score_max - raw_scores) / (score_max - score_min) * 100.0
        else:
            norm_scores = np.zeros(len(raw_scores))

        df_enriched["is_anomaly"] = predictions == -1
        df_enriched["anomaly_score"] = np.round(norm_scores, 1)

        # Anomaly band categorization
        conditions = [
            df_enriched["anomaly_score"] >= 85.0,
            df_enriched["anomaly_score"] >= 65.0,
        ]
        choices = ["CRITICAL", "MONITORING"]
        df_enriched["anomaly_band"] = np.select(conditions, choices, default="NORMAL")

        # Explainability: identify top contributing features for outliers
        reasons = []
        for idx, row in df_enriched.iterrows():
            factor_list = []
            if row["is_weekend"] == 1:
                factor_list.append("Weekend posting")
            if row["missing_dimension_flag"] == 1:
                factor_list.append("Direct project cost missing WBS/Project")
            if abs(row["amount_zscore_by_account"]) > 2.0:
                factor_list.append(f"Account amount {row['amount_zscore_by_account']:.1f}σ from mean")
            if row["is_round_thousand"] == 1:
                factor_list.append("Round thousand amount (>10k NOK)")
            if row["days_to_period_end"] <= 2:
                factor_list.append("Posted at month-end deadline")
            if not factor_list:
                factor_list.append("Statistical multi-factor inlier")
            reasons.append("; ".join(factor_list))

        df_enriched["explanation"] = reasons
        return df_enriched

def run_anomaly_detection(data_dir: str = "erp_data_2026_10") -> pd.DataFrame:
    """
    Convenience runner to load GL data, run detection, and return flagged candidates.
    """
    pq_lines = os.path.join(data_dir, "gl_journal_lines.parquet")
    csv_lines = os.path.join(data_dir, "gl_journal_lines.csv")
    pq_entries = os.path.join(data_dir, "gl_journal_entries.parquet")
    csv_entries = os.path.join(data_dir, "gl_journal_entries.csv")

    df_lines = pd.read_parquet(pq_lines) if os.path.exists(pq_lines) else pd.read_csv(csv_lines)
    df_entries = pd.read_parquet(pq_entries) if os.path.exists(pq_entries) else pd.read_csv(csv_entries)

    merged = df_lines.merge(df_entries, on="entry_id", how="left")
    detector = CloseAnomalyDetector(contamination=0.08)
    results = detector.fit_predict(merged)
    return results

if __name__ == "__main__":
    results = run_anomaly_detection("erp_data_2026_10")
    anomalies = results[results["anomaly_score"] >= 65.0]
    print(f"Detected {len(anomalies)} anomalies (score >= 65):")
    for _, row in anomalies.iterrows():
        print(f"[{row['entry_id']}] Account: {row['account_number']} | NOK: {row['amount_nok']:,.2f} | Score: {row['anomaly_score']} | Band: {row['anomaly_band']} | Reason: {row['explanation']}")
