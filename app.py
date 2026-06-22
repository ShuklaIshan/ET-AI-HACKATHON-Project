import streamlit as st
import pandas as pd
import plotly.express as px

from prince.fleet_advisor import (
    process_fleet,
    calculate_savings,
    calculate_carbon,
    calculate_roi
)

st.set_page_config(page_title="EVision AI")

st.title("⚡ EVision AI")

st.subheader("Fleet Electrification Advisor")

df = pd.read_csv("data/fleet_data.csv")

df = process_fleet(df)

df = calculate_savings(df)

df = calculate_carbon(df)

df = calculate_roi(df)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Annual Savings",
    f"₹{int(df['Annual_Savings'].sum()):,}"
)

col2.metric(
    "Fleet Size",
    len(df)
)

col3.metric(
    "EV Ready Vehicles",
    len(df[df["EV_Readiness"] > 70])
)

st.metric(
    "Annual CO₂ Reduction",
    f"{df['CO2_Reduction'].sum():.1f} Tons"
)

st.subheader("Fleet Recommendations")

st.dataframe(
    df[
        [
            "Vehicle_ID",
            "Vehicle_Type",
            "EV_Readiness",
            "Recommended_EV",
            "Annual_Savings",
            "CO2_Reduction"
        ]
    ]
)

best_vehicle = df.loc[
    df["Annual_Savings"].idxmax()
]

st.success(
    f"""
    AI Recommendation:
    
    Replace {best_vehicle['Vehicle_ID']}
    with {best_vehicle['Recommended_EV']}.

    Expected Annual Savings:
    ₹{int(best_vehicle['Annual_Savings']):,}
    """
)

st.subheader("Fuel vs Electricity Cost Comparison")

cost_df = df[
    [
        "Vehicle_ID",
        "Fuel_Cost_Year",
        "Electricity_Cost_Year"
    ]
]

fig = px.bar(
    cost_df,
    x="Vehicle_ID",
    y=[
        "Fuel_Cost_Year",
        "Electricity_Cost_Year"
    ],
    barmode="group",
    title="Annual Cost Comparison"
)

st.plotly_chart(fig, use_container_width=True)