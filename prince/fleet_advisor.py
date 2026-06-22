import pandas as pd

def calculate_readiness(distance, age):

    score = 20

    if distance < 150:
        score += 50

    if age > 3:
        score += 30

    return min(score, 100)

def recommend_ev(vehicle_type):

    if vehicle_type == "Truck":
        return "Tata Ace EV"

    elif vehicle_type == "Van":
        return "Mahindra eSupro"

    return "Electric Forklift"

def process_fleet(df):

    df["EV_Readiness"] = df.apply(
        lambda row: calculate_readiness(
            row["Daily_Distance"],
            row["Age"]
        ),
        axis=1
    )

    df["Recommended_EV"] = df["Vehicle_Type"].apply(recommend_ev)

    return df
def calculate_savings(df):

    df["Fuel_Cost_Year"] = (
        df["Daily_Distance"] *
        365 *
        df["Fuel_Price"] /
        df["Fuel_Efficiency"]
    )

    df["Electricity_Cost_Year"] = (
        df["Daily_Distance"] *
        365 *
        2
    )

    df["Annual_Savings"] = (
        df["Fuel_Cost_Year"] -
        df["Electricity_Cost_Year"]
    )

    return df

def calculate_carbon(df):

    df["CO2_Reduction"] = (
        df["Daily_Distance"] *
        365 *
        0.002
    )

    return df