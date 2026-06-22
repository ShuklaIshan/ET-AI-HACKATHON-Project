import pandas as pd

from modules.traceability_engine import find_affected_vehicles

fleet_df = pd.read_csv("data/fleet_data.csv")


def calculate_risk(batch_id):

    vehicles = find_affected_vehicles(batch_id)

    result = []

    for vehicle in vehicles:

        row = fleet_df[
            fleet_df["vehicle_id"] == vehicle
        ].iloc[0]

        battery_temp = row["battery_temp"]
        ambient_temp = row["ambient_temp"]

        risk_score = (
            battery_temp * 0.7
            +
            ambient_temp * 0.3
        )

        if risk_score > 45:
            risk = "CRITICAL"

        elif risk_score > 35:
            risk = "HIGH"

        elif risk_score > 25:
            risk = "MEDIUM"

        else:
            risk = "LOW"

        result.append({
            "vehicle_id": vehicle,
            "risk": risk,
            "score": float(round(risk_score, 2))
        })

    return result


def get_vehicle_risks(batch_id):
    return calculate_risk(batch_id)