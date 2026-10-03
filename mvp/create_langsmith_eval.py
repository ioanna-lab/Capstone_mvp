"""
LangSmith Evaluation Dataset Creator
Creates the lease-review-eval dataset with examples from the ground truth CSV.
Run this once to set up the evaluation dataset in LangSmith.

Usage:
    cd mvp
    python3 create_langsmith_eval.py
"""

import os
import csv
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langsmith import Client


def create_eval_dataset():
    client = Client()

    # check if dataset already exists
    try:
        existing = list(client.list_datasets(dataset_name="lease-review-eval"))
        if existing:
            print(f"Dataset 'lease-review-eval' already exists (ID: {existing[0].id})")
            print("Delete it in LangSmith UI first if you want to recreate it.")
            return existing[0].id
    except Exception:
        pass

    # create dataset
    dataset = client.create_dataset(
        "lease-review-eval",
        description=(
            "Lease extraction evaluation set for the AI Lease Review Assistant. "
            "Portuguese commercial leases with known ground truth. "
            "Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta"
        ),
    )
    print(f"Created dataset: lease-review-eval (ID: {dataset.id})")

    examples_added = 0

    # load from ground truth CSV if available
    gt_path = Path("data/leases/synthetic/ground_truth.csv")
    if gt_path.exists():
        with open(gt_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # select representative examples from each category
        categories_seen = set()
        selected = []
        for row in rows:
            cat = row.get("category", "")
            if cat not in categories_seen:
                categories_seen.add(cat)
                selected.append(row)
            if len(selected) >= 10:
                break

        for row in selected:
            client.create_example(
                inputs={
                    "filename": row.get("filename", ""),
                    "category": row.get("category", ""),
                    "property_type": row.get("property_type", ""),
                },
                outputs={
                    "tenant_name": row.get("tenant_name", ""),
                    "landlord_name": row.get("landlord_name", ""),
                    "lease_commencement_date": row.get("lease_commencement_date", ""),
                    "lease_expiry_date": row.get("lease_expiry_date", ""),
                    "rent_amount": row.get("rent_amount", ""),
                    "break_option_date": row.get("break_option_date", ""),
                    "expected_risk_level": row.get("expected_risk_level", ""),
                    "expected_flags": row.get("expected_flags", ""),
                    "has_nif_tenant": row.get("has_nif_tenant", ""),
                    "has_financas_clause": row.get("has_financas_clause", ""),
                    "stamp_duty_on_tenant": row.get("stamp_duty_on_tenant", ""),
                },
                dataset_id=dataset.id,
            )
            examples_added += 1
            print(f"  Added: {row.get('filename', '')} ({row.get('category', '')})")

    else:
        # fallback: add 3 hardcoded examples from the known synthetic corpus
        examples = [
            {
                "inputs": {
                    "filename": "PT_0001_office_Porto.pdf",
                    "category": "standard_office",
                    "property_type": "office",
                },
                "outputs": {
                    "tenant_name": "Porto Digital Solutions Lda.",
                    "expected_risk_level": "low",
                    "expected_flags": "none",
                    "has_nif_tenant": "yes",
                    "has_financas_clause": "yes",
                    "stamp_duty_on_tenant": "no",
                },
            },
            {
                "inputs": {
                    "filename": "PT_0076_break_option.pdf",
                    "category": "break_option_issue",
                    "property_type": "office",
                },
                "outputs": {
                    "expected_risk_level": "high",
                    "expected_flags": "dilapidations_survival_on_break",
                    "has_nif_tenant": "yes",
                    "has_financas_clause": "yes",
                    "stamp_duty_on_tenant": "no",
                },
            },
            {
                "inputs": {
                    "filename": "PT_0186_compliance_issue.pdf",
                    "category": "compliance_issue",
                    "property_type": "retail",
                },
                "outputs": {
                    "expected_risk_level": "high",
                    "expected_flags": "stamp_duty_on_tenant|notice_period_below_statutory",
                    "stamp_duty_on_tenant": "yes",
                    "notice_below_statutory": "yes",
                },
            },
        ]
        for ex in examples:
            client.create_example(
                inputs=ex["inputs"],
                outputs=ex["outputs"],
                dataset_id=dataset.id,
            )
            examples_added += 1
            print(f"  Added: {ex['inputs']['filename']}")

    print(f"\nDataset ready: {examples_added} examples added")
    print(f"Dataset ID: {dataset.id}")
    print(f"\nView at: https://smith.langchain.com")
    print("Click 'Datasets & Experiments' in the left sidebar")
    return dataset.id


if __name__ == "__main__":
    create_eval_dataset()
