import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
from predict_future import get_predictions


st.set_page_config(page_title="AquaTrack", layout="wide")

# CSS for professional button styles
st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: #005f73;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-size: 1.1rem;
        transition: background-color 0.3s ease;
        border: none;
        cursor: pointer;
    }
    div.stButton > button:first-child:hover {
        background-color: #0a9396;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CRITICAL_THRESHOLD = 3.0  # meters for alerts

# Splash screen + quote
if "splash_displayed" not in st.session_state:
    splash_placeholder = st.empty()
    combined_html = """
    <div style="
        background: linear-gradient(45deg, #00b4db, #0083b0);
        height: 300px;
        border-radius: 15px;
        margin: 30px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
        padding: 20px;
    ">
        <div style="font-size: 3em; font-weight: bold; margin-bottom: 10px;">
            AquaTrack
        </div>
        <div style="
            font-style: italic; 
            color: #aad4f5;
            font-size: 1.2em;
            max-width: 600px;
        ">
            "Water is life – Preserve it for future generations."
        </div>
    </div>
    """
    splash_placeholder.markdown(combined_html, unsafe_allow_html=True)
    time.sleep(2)
    splash_placeholder.empty()
    st.session_state.splash_displayed = True
df = pd.read_csv("/Users/sruthiuma/Documents/PrototypeSIH/dataset/monsoon_cleaned.csv")
df["VILLAGE"] = df["VILLAGE"].str.strip()
df["Date"] = pd.to_datetime(df["Date"])

if "dashboard_type" not in st.session_state:
    st.session_state.dashboard_type = None

if st.session_state.dashboard_type is None:
    st.title("AquaTrack - Groundwater Resource Evaluation")
    st.markdown("Monitor water levels in your village in real-time")

    villages = sorted(df["VILLAGE"].unique())
    villages_with_placeholder = ["select village"] +villages

    selected_village = st.selectbox(
        "Select Location",
        options=villages_with_placeholder,
        index=0,
        help="Select your village",
    )

    if selected_village == "Select Location":
        st.warning("Please select a village to continue.")
    else:
        st.session_state.selected_village = selected_village

        st.markdown("### Select Your Role to Continue")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.image(
                "/Users/sruthiuma/Documents/PrototypeSIH/assets/Farmers.jpg",
                caption="Farmers",
                use_container_width=True,
            )
            st.markdown(
                "**Farmers**\nI want to cultivate crops and know future water levels."
            )
            if st.button("See Levels - Farmers", key="btn_farmers"):
                st.session_state.dashboard_type = "Farmers"

        with col2:
            st.image(
                "/Users/sruthiuma/Documents/PrototypeSIH/assets/policymakers.jpg",
                caption="Policy Makers",
                use_container_width=True,
            )
            st.markdown(
                "**Policy Makers**\nI want to plan water management and policies."
            )
            if st.button("See Levels - Policy Makers", key="btn_policy"):
                st.session_state.dashboard_type = "Policy Makers"

        with col3:
            st.image(
                "/Users/sruthiuma/Documents/PrototypeSIH/assets/researcher.jpg",
                caption="Researchers",
                use_container_width=True,
            )
            st.markdown("**Researchers**\nI want detailed analysis and historical data.")
            if st.button("See Levels - Researchers", key="btn_research"):
                st.session_state.dashboard_type = "Researchers"

else:
    dashboard_type = st.session_state.dashboard_type
    selected_village = st.session_state.selected_village
    village_data = df[df["VILLAGE"].str.lower() == selected_village.lower()]

    if village_data.empty:
        st.warning("No data found for this village.")
    else:
        st.title("AquaTrack")
        st.success(f"Showing {dashboard_type} data for: {selected_village}")
        st.subheader(f"{dashboard_type} Dashboard - {selected_village}")

        time_ranges = []
        if dashboard_type == "Farmers":
            time_ranges = [
                {"label": "2016-2024", "start": pd.Timestamp("2016-01-01"), "end": pd.Timestamp("2024-12-31")},
                {"label": "2025-2026 (Predicted)", "start": pd.Timestamp("2025-01-01"), "end": pd.Timestamp("2026-12-31")},
            ]
        else:
            st.sidebar.subheader("Select Past Data Range")
            past_start = pd.Timestamp(st.sidebar.date_input("Past Start Date", village_data["Date"].min()))
            past_end = pd.Timestamp(st.sidebar.date_input("Past End Date", village_data["Date"].max()))
            time_ranges.append({"label": f"Past ({past_start.year}-{past_end.year})", "start": past_start, "end": past_end})

            st.sidebar.subheader("Select Future Prediction Range")
            future_start = pd.Timestamp(st.sidebar.date_input("Future Start Date", datetime(2025, 1, 1)))
            future_end = pd.Timestamp(st.sidebar.date_input("Future End Date", datetime(2026, 12, 31)))
            time_ranges.append({"label": f"Future ({future_start.year}-{future_end.year})", "start": future_start, "end": future_end})

        for tr in time_ranges:
            start, end, label = tr["start"], tr["end"], tr["label"]
            if "Predicted" in label or "Future" in label:
                data = get_predictions(selected_village, start, end)
                value_col = "Predicted_DTWl"
            else:
                data = village_data[(village_data["Date"] >= start) & (village_data["Date"] <= end)]
                value_col = "DTWL"

            st.subheader(f"{label} Groundwater Levels")
            if not data.empty:
                min_val = data[value_col].min()
                if min_val < CRITICAL_THRESHOLD:
                    st.error(f"⚠️ Alert: Critical groundwater level! Minimum depth {min_val:.2f}m below threshold.")
                else:
                    st.success(f"✅ Groundwater level within safe limits. Minimum depth {min_val:.2f}m.")

                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(data["Date"], data[value_col], marker="o", color="#1f77b4", label=label)
                ax.set_facecolor("#ffffff")
                ax.grid(True, linestyle="--", alpha=0.6)
                ax.set_xlabel("Date", color="#000000")
                ax.set_ylabel("Depth to Water Level (m)", color="#000000")
                ax.legend()
                plt.xticks(rotation=45, color="#000000")
                plt.yticks(color="#000000")
                st.pyplot(fig)

                st.markdown(
                    f"**Summary ({label}):**\n"
                    f"- Average Depth to Water Level: {data[value_col].mean():.2f} m\n"
                    f"- Minimum Depth to Water Level: {data[value_col].min():.2f} m\n"
                    f"- Maximum Depth to Water Level: {data[value_col].max():.2f} m"
                )

                recharge_data = data.sort_values("Date").copy()
                recharge_data["Recharge"] = recharge_data[value_col].shift(1) - recharge_data[value_col]
                if (end - start).days > 90:
                    recharge_data = recharge_data.set_index("Date")[["Recharge"]].resample("M").sum().reset_index()
                st.subheader(f"Estimated Recharge ({label})")
                if not recharge_data.empty:
                    fig_r, ax_r = plt.subplots(figsize=(10, 4))
                    ax_r.plot(recharge_data["Date"], recharge_data["Recharge"], marker="o", color="#2ca02c", label="Recharge (m)")
                    ax_r.axhline(0, color="#888888", linestyle="--", linewidth=1)
                    ax_r.set_xlabel("Date")
                    ax_r.set_ylabel("Recharge (m)")
                    ax_r.legend()
                    ax_r.grid(True, linestyle="--", alpha=0.6)
                    plt.xticks(rotation=45)
                    st.pyplot(fig_r)
                    st.info(f"Average Recharge ({label}): {recharge_data['Recharge'].mean():.2f} m")
                else:
                    st.warning(f"No recharge data available for {label}.")

                if dashboard_type != "Farmers":
                    csv = data.to_csv(index=False)
                    st.download_button(
                        label=f"Download {label} Data",
                        data=csv,
                        file_name=f"{selected_village}_{label.replace(' ', '_')}.csv",
                        mime="text/csv",
                    )
            else:
                st.warning(f"No data available for {label}.")

   #if st.button("Back to Role Selection"):
      # // st.session_state.dashboard_type = None
    if st.button("Back to Role Selection"):
      st.session_state['page'] = 'role_selection'
      st.session_state['dashboard_type'] = None
