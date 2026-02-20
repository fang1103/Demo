from __future__ import annotations

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

try:
    from multimodal_demo.operations import resilience_curve
    from multimodal_demo.optimization import Action, prioritize_actions
    from multimodal_demo.schema import build_demo_network
    from multimodal_demo.simulation import FailureScenario, simulate_cascading_failures
except ModuleNotFoundError as exc:
    raise SystemExit("Package import failed. Run with `PYTHONPATH=src streamlit run app.py` or install with `pip install -e .`.") from exc

st.set_page_config(page_title="Multimodal Resilience Demo", layout="wide")
st.title("Multimodal Infrastructure Resilience Demo")
st.caption("GIS + interdependency simulation + resilience analytics + action prioritization")

network = build_demo_network()
graph = network.to_graph(prefer_networkx=True)

st.sidebar.header("Scenario Controls")
initial_failure = st.sidebar.multiselect("Initial failed assets", options=list(graph.nodes), default=["compressor_1"])
degradation_rate = st.sidebar.slider("Degradation rate", 0.05, 1.0, 0.35, 0.05)
threshold = st.sidebar.slider("Failure threshold", 0.0, 1.0, 0.4, 0.05)
max_steps = st.sidebar.slider("Simulation steps", 1, 12, 5)
coupling_mode = st.sidebar.selectbox("Interdependency logic", ["linear", "threshold"])
optimizer = st.sidebar.selectbox("Optimization method", ["greedy", "exact"])
budget = st.sidebar.slider("Response budget", 10, 300, 120)

scenario = FailureScenario(
    failed_nodes=initial_failure,
    degradation_rate=degradation_rate,
    dependency_threshold=threshold,
    max_steps=max_steps,
    coupling_mode=coupling_mode,
)
history = simulate_cascading_failures(graph.copy(), scenario)
curve = resilience_curve(history, graph.copy())

left, right = st.columns((1, 1))
with left:
    st.subheader("Map View")
    node_df = pd.DataFrame(
        [
            {
                "id": node,
                "label": data["label"],
                "network_type": data["network_type"],
                "lat": data["latitude"],
                "lon": data["longitude"],
                "condition": data.get("condition", 1.0),
            }
            for node, data in graph.nodes(data=True)
        ]
    )
    final_failed = {node for nodes in history.values() for node in nodes}
    node_df.loc[node_df["id"].isin(final_failed), "condition"] = 0.0

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=node_df,
        get_position="[lon, lat]",
        get_radius=5000,
        get_fill_color="[255 * (1 - condition), 255 * condition, 80]",
        pickable=True,
    )
    st.pydeck_chart(
        pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=node_df["lat"].mean(), longitude=node_df["lon"].mean(), zoom=6),
            layers=[layer],
            tooltip={"text": "{label}\nType: {network_type}\nCondition: {condition}"},
        )
    )
    st.dataframe(node_df, use_container_width=True)

with right:
    st.subheader("Vulnerability + Resilience")
    curve_df = pd.DataFrame(curve)
    st.plotly_chart(px.line(curve_df, x="step", y=["service_ratio", "health_index"], markers=True, title="Resilience Curves"), use_container_width=True)
    st.plotly_chart(
        px.density_heatmap(
            node_df[["id", "network_type", "condition"]],
            x="network_type",
            y="id",
            z="condition",
            color_continuous_scale="RdYlGn",
            title="Asset Vulnerability Heatmap",
        ),
        use_container_width=True,
    )

st.subheader("Decision-Making Layer (Design / Expansion / Response / Recovery)")
actions = [
    Action("Install compressor redundancy", cost=80, impact_score=65, phase="design"),
    Action("Upgrade pipeline segment", cost=55, impact_score=40, phase="expansion"),
    Action("Deploy mobile generators", cost=45, impact_score=52, phase="response"),
    Action("Emergency telecom backup", cost=35, impact_score=34, phase="response"),
    Action("Accelerated repair crews", cost=60, impact_score=58, phase="recovery"),
]
selected = prioritize_actions(actions, budget=budget, strategy=optimizer)
st.write(f"Selected actions for budget **{budget}** using **{optimizer}** optimization:")
st.table(pd.DataFrame([a.__dict__ for a in selected]))

with st.expander("Simulation event log"):
    st.json(history)
