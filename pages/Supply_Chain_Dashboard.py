import streamlit as st
import pandas as pd
import plotly.express as px

from modules.defect_engine import simulate_defect
from modules.risk_engine import get_vehicle_risks

# -------------------------------
# PAGE CONFIG
# -------------------------------

st.set_page_config(
    page_title="Supply Chain Intelligence",
    page_icon="🔋",
    layout="wide"
)

# -------------------------------
# HEADER
# -------------------------------

st.title("🔋 Battery Traceability & Supply Chain Intelligence")

st.markdown(
    """
    Simulate battery manufacturing defects and identify affected vehicles
    with thermal risk assessment.
    """
)

# -------------------------------
# LOAD DATA
# -------------------------------

batch_df = pd.read_csv("data/battery_batches.csv")

batch_list = batch_df["batch_id"].tolist()

selected_batch = st.selectbox(
    "Select Battery Batch",
    batch_list
)

# -------------------------------
# SIMULATE BUTTON
# -------------------------------

if st.button("🚨 Simulate Defect"):

    summary = simulate_defect(selected_batch)

    # Alert Banner
    st.error(
        f"⚠ Manufacturing defect detected in batch {selected_batch}"
    )

    st.divider()

    # -------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------

    st.subheader("Executive Summary")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Supplier",
            summary["supplier"]
        )

    with col2:
        st.metric(
            "Affected Vehicles",
            summary["affected_vehicles"]
        )

    with col3:
        st.metric(
            "Critical",
            summary["critical"]
        )

    with col4:
        st.metric(
            "Medium",
            summary["medium"]
        )

    with col5:
        st.metric(
            "Low",
            summary["low"]
        )

    st.divider()

    # -------------------------------
    # RISK DISTRIBUTION CHART
    # -------------------------------

    st.subheader("Risk Distribution")

    chart_df = pd.DataFrame({
        "Risk": ["Critical", "Medium", "Low"],
        "Count": [
            summary["critical"],
            summary["medium"],
            summary["low"]
        ]
    })

    fig = px.bar(
        chart_df,
        x="Risk",
        y="Count",
        title="Vehicle Risk Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # -------------------------------
    # VEHICLE RISK TABLE
    # -------------------------------

    st.subheader("Vehicle Risk Assessment")

    risks = get_vehicle_risks(selected_batch)

    risk_df = pd.DataFrame(risks)

    st.dataframe(
        risk_df,
        use_container_width=True
    )

    st.success(
        f"Defect detected in {selected_batch}. "
        f"{summary['affected_vehicles']} vehicles identified."
    )