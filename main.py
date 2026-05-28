import time
import pandas as pd
import streamlit as st
import plotly.express as px

from simulation import run_simulation
from routes import ROUTES
from behaviors import BEHAVIOR_PROFILES

# page config

st.set_page_config(
    page_title="Jeepney Fuel Consumption Simulator",
    layout="wide"
)

# TITLE
st.title("🚐 Jeepney Fuel Consumption Simulator")

st.markdown("""
Real-time fuel consumption simulation for a modern
Philippine jeepney using driver behavior and vehicle dynamics.
""")


# sidebar
st.sidebar.header("Simulation Controls")

selected_route = st.sidebar.selectbox(
    "Select Route",
    list(ROUTES.keys())
)

selected_behavior = st.sidebar.selectbox(
    "Driving Behavior",
    list(BEHAVIOR_PROFILES.keys())
)

simulation_speed = st.sidebar.slider(
    "Simulation Speed",
    min_value=0.01,
    max_value=1.0,
    value=0.10,
    step=0.01
)

run_button = st.sidebar.button("▶ Run Simulation")

# route + behavio
route_data = ROUTES[selected_route]
behavior_data = BEHAVIOR_PROFILES[selected_behavior]


# tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Dashboard",
    "🚐 Real-Time Simulation",
    "📁 Raw Data"
])


# run simulation
if run_button:

    # run physics simulation

    log, total_fuel, fuel_economy, total_distance = run_simulation(
        segments=route_data["segments"],
        behavior_name=selected_behavior,
        behavior=behavior_data
    )


    # dataframe
    df = pd.DataFrame(log)

    if df.empty:
        st.error("Simulation produced no data.")
        st.stop()

    # tab 1 - dashboard
    with tab1:

        st.subheader("Simulation Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Distance",
            f"{total_distance/1000:.2f} km"
        )

        col2.metric(
            "Fuel Used",
            f"{total_fuel:.4f} L"
        )

        col3.metric(
            "Fuel Economy",
            f"{fuel_economy:.2f} km/L"
        )

        col4.metric(
            "Behavior",
            selected_behavior
        )

        st.divider()


        # speed graph
        st.subheader("Speed vs Time")

        fig_speed = px.line(
            df,
            x="time",
            y="speed_kmh"
        )

        st.plotly_chart(
            fig_speed,
            use_container_width=True
        )


        # fuel graph
        st.subheader("Fuel Consumption")

        fig_fuel = px.line(
            df,
            x="time",
            y="total_fuel_L"
        )

        st.plotly_chart(
            fig_fuel,
            use_container_width=True
        )


        # traction force
        st.subheader("Traction Force")

        fig_force = px.line(
            df,
            x="time",
            y="F_traction_N"
        )

        st.plotly_chart(
            fig_force,
            use_container_width=True
        )


    # tab2 - real time simulation
    with tab2:

        st.subheader("Real-Time Vehicle Simulation")


        # placeholders
        road_placeholder = st.empty()

        telemetry_col1, telemetry_col2, telemetry_col3 = st.columns(3)

        speed_placeholder = telemetry_col1.empty()
        fuel_placeholder = telemetry_col2.empty()
        phase_placeholder = telemetry_col3.empty()

        progress_placeholder = st.progress(0)

        live_chart_placeholder = st.empty()


        # live chart data
        live_speed_data = pd.DataFrame(
            columns=["time", "speed_kmh"]
        )

        total_distance_m = df["distance_m"].max()


        # real time loop
        for i, row in df.iterrows():

            # road anim
            progress = row["distance_m"] / total_distance_m

            position = int(progress * 50)

            if position >= 50:
                position = 49

            road = ["="] * 50

            road[position] = "🚐"

            road_display = "".join(road)

            road_placeholder.text(road_display)


            # live telemetry
            speed_placeholder.metric(
                "Speed",
                f"{row['speed_kmh']:.2f} km/h"
            )

            fuel_placeholder.metric(
                "Fuel Used",
                f"{row['total_fuel_L']:.4f} L"
            )

            phase_placeholder.metric(
                "Driving Phase",
                row["phase"]
            )


            # progrss bar
            progress_placeholder.progress(
                min(float(progress), 1.0)
            )


            # live chart updt
            new_row = pd.DataFrame({
                "time": [row["time"]],
                "speed_kmh": [row["speed_kmh"]]
            })

            live_speed_data = pd.concat(
                [live_speed_data, new_row],
                ignore_index=True
            )

            live_chart = px.line(
                live_speed_data,
                x="time",
                y="speed_kmh",
                title="Live Speed"
            )

            live_chart_placeholder.write(live_chart)

        
            # simulation speed
            time.sleep(simulation_speed)

        st.success("Simulation Complete!")


    # tab3 - raw data
    with tab3:

        st.subheader("Simulation Data")

        st.dataframe(
            df,
            use_container_width=True
        )

        csv = df.to_csv(index=False)

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="simulation_results.csv",
            mime="text/csv"
        )

# before run
else:

    st.info("Press 'Run Simulation' to begin.")