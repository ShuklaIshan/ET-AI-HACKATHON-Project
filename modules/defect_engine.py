import pandas as pd
from modules.traceability_engine import get_supplier
from modules.risk_engine import calculate_risk

batch_df = pd.read_csv("data/battery_batches.csv")

def simulate_defect(batch_id):

    batch_df.loc[
        batch_df["batch_id"] == batch_id,
        "status"
    ] = "Defective"

    risks = calculate_risk(batch_id)
    supplier = get_supplier(batch_id)

    summary = {
        "supplier": supplier,
        "batch": batch_id,
        "affected_vehicles": len(risks),
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for item in risks:

        risk = item["risk"].lower()

        summary[risk] += 1

    return summary