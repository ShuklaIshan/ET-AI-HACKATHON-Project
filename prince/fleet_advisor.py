import pandas as pd
import numpy as np

# --- INDUSTRIAL VEHICLE CONFIGURATIONS ---
VEHICLE_CONFIGS = {
    "Bike / Delivery": {
        "replacement": "Hero Electric Nyx",
        "ev_cost": 90000,
        "battery_cost": 35000,
        "ev_efficiency": 0.04,   
        "v2g_potential": 5000    
    },
    "Three-Wheeler / Cargo Loader": {
        "replacement": "Mahindra Treo Zor",
        "ev_cost": 350000,
        "battery_cost": 120000,
        "ev_efficiency": 0.12,
        "v2g_potential": 12000
    },
    "Light Truck": {
        "replacement": "Tata Ace EV",
        "ev_cost": 650000,
        "battery_cost": 250000,
        "ev_efficiency": 0.20,
        "v2g_potential": 25000
    },
    "Medium Van": {
        "replacement": "Mahindra eSupro Cargo",
        "ev_cost": 850000,
        "battery_cost": 350000,
        "ev_efficiency": 0.25,
        "v2g_potential": 30000
    },
    "Heavy Duty Truck": {
        "replacement": "IPL Tech Electric 55T",
        "ev_cost": 3500000,
        "battery_cost": 1500000,
        "ev_efficiency": 1.20,
        "v2g_potential": 90000
    },
    "Forklift / Tow Truck": {
        "replacement": "Godrej Electric Series",
        "ev_cost": 500000,
        "battery_cost": 180000,
        "ev_efficiency": 0.15,
        "v2g_potential": 15000
    }
}

COMMERCIAL_ELECTRICITY_TARIFF = 8.0  # ₹ per kWh

def calculate_readiness_score(row):
    distance = row.get("Daily_Distance", 0)
    age = row.get("Age", 0)
    
    # Balanced baseline score to allow real variance
    score = 10
    
    # 1. Daily Mileage Efficiency Windows
    if 80 <= distance <= 250:
        score += 50  # Golden range for operational fuel savings payback
    elif 40 <= distance < 80:
        score += 30  # Moderate utility return
    elif distance > 250:
        score += 15  # Range anxiety / high-frequency charging needed
    else:
        score += 5   # Low usage doesn't justify high upfront EV asset costs
        
    # 2. Capital Depreciation Lifecycle (Age)
    if age >= 5:
        score += 40  # Old polluting vehicle near end of life; perfect to scrap
    elif 2 <= age < 5:
        score += 20  # Mid-life asset cycle
    else:
        score += 0   # Brand new vehicle; financial waste to scrap or sell right now
        
    return min(score, 100)

def process_fleet(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    df["Vehicle_Type"] = df["Vehicle_Type"].apply(lambda x: x if x in VEHICLE_CONFIGS else "Light Truck")
    df["Quantity"] = df["Quantity"].fillna(1).astype(int)
    
    # 1. Readiness Scoring & Vehicle Suggestions
    df["EV_Switch_Score"] = df.apply(calculate_readiness_score, axis=1)
    df["Recommended_EV"] = df["Vehicle_Type"].apply(lambda x: VEHICLE_CONFIGS[x]["replacement"])
    
    # 2. Scaling Financial Metrics by Quantity
    df["Fuel_Cost_Year"] = (((df["Daily_Distance"] * 365 * df["Fuel_Price"]) / df["Fuel_Efficiency"].replace(0, np.nan)).fillna(0)) * df["Quantity"]
    df["Electricity_Cost_Year"] = df.apply(
        lambda row: row["Daily_Distance"] * 365 * VEHICLE_CONFIGS[row["Vehicle_Type"]]["ev_efficiency"] * COMMERCIAL_ELECTRICITY_TARIFF,
        axis=1
    ) * df["Quantity"]
    
    df["Operational_Savings_Year"] = df["Fuel_Cost_Year"] - df["Electricity_Cost_Year"]
    
    # 3. Smart Charging Income Scaled by Quantity
    df["V2G_Revenue_Year"] = df.apply(
        lambda row: VEHICLE_CONFIGS[row["Vehicle_Type"]]["v2g_potential"] * (1 + (row.get("Idle_Time_Hours", 3.5) / 24)),
        axis=1
    ) * df["Quantity"]
    
    df["Total_Annual_Savings"] = df["Operational_Savings_Year"] + df["V2G_Revenue_Year"]
    
    # 4. Payback timeline relative to batch investment cost
    df["Time_to_Earn_Back_Investment"] = df.apply(
        lambda row: round((VEHICLE_CONFIGS[row["Vehicle_Type"]]["ev_cost"] * row["Quantity"]) / row["Total_Annual_Savings"], 1) 
        if row["Total_Annual_Savings"] > 0 else np.inf,
        axis=1
    )
    
    # 5. Ecological Impact Scaled by Quantity
    df["CO2_Pollution_Saved"] = (
        (((df["Daily_Distance"] * 365) / df["Fuel_Efficiency"].replace(0, np.nan)) * 2.68 / 1000).fillna(0) * df["Quantity"]
    ).round(1)
    
    # 6. Battery Resale Liquid Value Scaled by Quantity
    df["Battery_Resale_Value"] = df.apply(
        lambda row: max(VEHICLE_CONFIGS[row["Vehicle_Type"]]["battery_cost"] * 0.18 - (row["Age"] * 10000), 20000),
        axis=1
    ) * df["Quantity"]
    
    return df