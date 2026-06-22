import streamlit as st
import pandas as pd
import plotly.express as px

from prince.fleet_advisor import process_fleet, VEHICLE_CONFIGS

st.set_page_config(page_title="EVision AI", layout="wide", page_icon="⚡")

if 'defect_triggered' not in st.session_state:
    st.session_state.defect_triggered = False
if 'my_fleet_list' not in st.session_state:
    st.session_state.my_fleet_list = []  
if 'analyzed_fleet' not in st.session_state:
    st.session_state.analyzed_fleet = None  

st.sidebar.title("⚡ EVision AI")
app_mode = st.sidebar.radio("Go to Page:", ["📋 Fleet EV Switch Advisor", "🔋 Battery Safety & Tracking Portal"])
st.sidebar.markdown("---")

# ==========================================
# PAGE 1: FLEET EV SWITCH ADVISOR
# ==========================================
if app_mode == "📋 Fleet EV Switch Advisor":
    st.title("⚡ EVision AI")
    st.subheader("Interactive Fleet Builder & Planner")
    st.markdown("Add your fleet details below. The system will analyze ranges, age, costs, and flag whether a switch is viable.")

    # --- SIDEBAR PANEL FOR SYSTEM DATA ENTRY ---
    st.sidebar.header("📋 Add a Vehicle to Your Fleet")
    custom_id = st.sidebar.text_input("Vehicle Batch Name / ID", value=f"Batch-{len(st.session_state.my_fleet_list) + 1}")
    v_type = st.sidebar.selectbox("Vehicle Category", list(VEHICLE_CONFIGS.keys()))
    quantity = st.sidebar.number_input("Number of Vehicles (Quantity)", min_value=1, value=5, step=1)
    daily_distance = st.sidebar.number_input("Daily Distance per Vehicle (km)", min_value=1, value=120)
    fuel_efficiency = st.sidebar.number_input("Current Fuel Mileage (km/liter)", min_value=1.0, value=12.0, step=0.5)
    fuel_price = st.sidebar.number_input("Fuel Price (₹/Liter)", min_value=1.0, value=95.0, step=0.5)
    age = st.sidebar.number_input("Vehicle Age (Years)", min_value=0, value=2)

    # --- INPUT VALIDATION AND HARD REJECTION SYSTEM ---
    validation_passed = True

    if v_type == "Heavy Duty Truck" and fuel_efficiency > 10.0:
        st.sidebar.error("❌ REJECTED: Heavy Duty Trucks cannot run at >10 km/L. Adjust for accurate calculations.")
        validation_passed = False

    if daily_distance > 600:
        st.sidebar.error("❌ REJECTED: 600+ km daily running exceeds daily commercial EV battery ranges.")
        validation_passed = False

    if v_type == "Bike / Delivery" and fuel_efficiency < 15.0:
        st.sidebar.error("❌ REJECTED: Delivery bikes cannot have gas mileage below 15 km/L.")
        validation_passed = False

    # Process Save Action only if all safety checks pass
    if st.sidebar.button("➕ Save and Add Vehicle") and validation_passed:
        st.session_state.my_fleet_list.append({
            "Vehicle_ID": custom_id,
            "Vehicle_Type": v_type,
            "Quantity": int(quantity),
            "Daily_Distance": daily_distance,
            "Fuel_Efficiency": fuel_efficiency,
            "Fuel_Price": fuel_price,
            "Age": age,
            "Idle_Time_Hours": 3.5
        })
        st.sidebar.success(f"Added batch '{custom_id}' ({quantity} units) to tracking stack!")

    if st.sidebar.button("🗑️ Reset Fleet List"):
        st.session_state.my_fleet_list = []
        st.session_state.analyzed_fleet = None
        st.rerun()

    # --- PREVIEW REGISTRY STRUCTURE ---
    st.subheader("Your Saved Vehicles Registry")
    if len(st.session_state.my_fleet_list) == 0:
        st.info("💡 Your fleet list is currently empty. Add entries via the left sidebar panel configuration.")
    else:
        df_preview = pd.DataFrame(st.session_state.my_fleet_list)
        df_preview.index = df_preview.index + 1
        df_preview.columns = ["Vehicle Batch Name", "Vehicle Category Type", "Quantity (Units)", "Daily Distance (km)", "Current Fuel Mileage (km/L)", "Fuel Price (₹/L)", "Asset Age (Years)", "Idle Hours"]
        st.dataframe(df_preview[["Vehicle Batch Name", "Vehicle Category Type", "Quantity (Units)", "Daily Distance (km)", "Current Fuel Mileage (km/L)"]], use_container_width=True)
        
        st.markdown("---")
        if st.button("🚀 Run Complete Analysis on My Fleet"):
            raw_temp_df = pd.DataFrame(st.session_state.my_fleet_list)
            st.session_state.analyzed_fleet = process_fleet(raw_temp_df)

    # --- COMPLETE ANALYSIS RENDERING MODULES ---
    if st.session_state.analyzed_fleet is not None:
        df_calculated = st.session_state.analyzed_fleet.copy()
        
        total_units = int(df_calculated['Quantity'].sum())
        # Filter check using our dynamic threshold target
        ready_count = len(df_calculated[df_calculated['EV_Switch_Score'] >= 60])
        annual_savings = int(df_calculated['Total_Annual_Savings'].sum())
        carbon_reduction = df_calculated['CO2_Pollution_Saved'].sum()

        st.markdown("---")
        st.success("📊 **AI Strategic Analysis Generated Below!**")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Fleet Money Saved / Year", f"₹{annual_savings:,}")
        col2.metric("Total Asset Fleet Count", f"{total_units} Units")
        col3.metric("Ready Batches to Switch", f"{ready_count} Categories")

        col4, col5, col6 = st.columns(3)
        col4.metric("Old Batteries Resale Cash-Back", f"₹{int(df_calculated['Battery_Resale_Value'].sum()):,}")
        col5.metric("Extra Smart Charging Income", f"₹{int(df_calculated['V2G_Revenue_Year'].sum()):,}")
        col6.metric("Total CO₂ Pollution Saved", f"{carbon_reduction:.1f} Tons")

        st.subheader("Your Personalized EV Transition Roadmap")
        
        # Determine strict readiness markers dynamically
        df_calculated["Switch_Status"] = df_calculated["EV_Switch_Score"].apply(
            lambda score: "🟢 READY" if score >= 60 else "🔴 NOT READY"
        )
        
        df_display = df_calculated[[
            "Vehicle_ID", "Vehicle_Type", "Quantity", "Switch_Status", "EV_Switch_Score", "Recommended_EV", 
            "Total_Annual_Savings", "Time_to_Earn_Back_Investment", "CO2_Pollution_Saved"
        ]].copy()
        
        df_display.index = range(1, len(df_display) + 1)
        df_display.columns = [
            "Vehicle Batch Name", "Vehicle Category Type", "Quantity (Units)", "Ready to Switch Status", "EV Switch Score (%)", "Recommended Model", 
            "Total Yearly Savings (₹)", "Years to Get Money Back (Years)", "CO₂ Pollution Saved (Tons)"
        ]
        st.dataframe(df_display, use_container_width=True)

        st.subheader("Total Batch Expense Comparison (Lower is Better)")
        fig = px.bar(
            df_calculated, x="Vehicle_ID", y=["Fuel_Cost_Year", "Electricity_Cost_Year"], barmode="group",
            labels={"value": "Total Yearly Costs (₹)", "variable": "Expense Type", "Vehicle_ID": "Vehicle Batch Designation"},
            color_discrete_map={"Fuel_Cost_Year": "#EF553B", "Electricity_Cost_Year": "#00CC96"}
        )
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# PAGE 2: BATTERY SAFETY & TRACKING PORTAL
# ==========================================
else:
    st.title("⚡ EVision AI Safety Network")
    st.subheader("Battery Traceability & Safety Portal")
    st.markdown("See how our closed-loop architecture tracking secures components directly mapped to your created custom vehicles list.")

    st.markdown("### 🏭 Battery Manufacturer Simulation Console")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💥 Simulate Factory Defect Report"): st.session_state.defect_triggered = True
    with c2:
        if st.button("🔄 Clear Alarms & Normalize Network"): st.session_state.defect_triggered = False

    st.markdown("---")

    if st.session_state.analyzed_fleet is not None:
        available_vehicles = st.session_state.analyzed_fleet["Vehicle_ID"].tolist()
        if "Flagged-Sample-Truck-X" not in available_vehicles:
            available_vehicles.insert(0, "Flagged-Sample-Truck-X")
    else:
        available_vehicles = ["Flagged-Sample-Truck-X", "Demo-Vehicle-02", "Demo-Vehicle-05"]

    if st.session_state.defect_triggered:
        st.error(
            "🚨 **CRITICAL ALARM: LIVE INDUSTRIAL RISK MATCH DETECTED**\n\n"
            "* **Manufacturer Update:** Factory reports risk on Cell Production Line 4 (Lot-NMC-902).\n"
            "* **Your Fleet Status:** Warning! This bad factory batch matches components mapped to **Flagged-Sample-Truck-X**.\n"
            "* **Geospatial Context Intervene:** Vehicle is currently driving through **Rajasthan under a 45°C extreme heatwave**. Due to surrounding climate risk, tracking priority updated to **CRITICAL ACTION REQUIRED**."
        )
    else:
        st.success("🟢 **All System Nodes Clear:** Battery sensors, factory lot codes, and fleet assets match normal safe operation guidelines.")

    st.subheader("Select Vehicle from Your Checked Fleet Inventory")
    asset_selection = st.selectbox("Choose a vehicle to scan its live battery health passport:", available_vehicles)

    col_x, col_y = st.columns([2, 1])
    with col_y:
        st.markdown("#### Live Sensor Readings")
        if "Flagged" in asset_selection and st.session_state.defect_triggered:
            cycles = st.slider("Total Battery Charge Cycles Used", 100, 2000, 1420)
            temp = st.slider("Live Core Battery Temperature (°C)", 15, 65, 54)
        else:
            cycles = st.slider("Total Battery Charge Cycles Used", 100, 2000, 320)
            temp = st.slider("Live Core Battery Temperature (°C)", 15, 65, 28)

    with col_x:
        rem_life = max(100 - (cycles * 0.012) - (max(temp - 35, 0) * 1.5), 10.0)
        st.markdown(f"#### 🪪 Digital Battery Passport: {asset_selection}")
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Battery Remaining Life", f"{round(rem_life, 1)}%")
        if "Flagged" in asset_selection and st.session_state.defect_triggered:
            k2.markdown("<h4 style='color:red;'>🚨 EMERGENCY WARNING</h4>", unsafe_allow_html=True)
            k3.metric("Action Required Within", "Immediate (<24 Hours)")
            st.warning("⚠️ **Safety Action:** System has routed emergency cooling updates straight to this asset's thermal control unit.")
        else:
            k2.markdown("<h4 style='color:green;'>🟢 OPTIMAL SAFE HEALTH</h4>", unsafe_allow_html=True)
            k3.metric("Action Required Within", "None (Healthy)")

        st.table(pd.DataFrame({
            "Battery Profile Field": ["Unique Registry ID Code", "Internal Cell Component Lot Code", "Manufacturing Eco-Carbon Weight"],
            "Passport Secure Record": ["CELL-BATT-UNIQ-8849", "Batch-NMC-902" if "Flagged" in asset_selection else "Batch-NMC-104", "4.2 kg CO₂e per kWh"]
        }))