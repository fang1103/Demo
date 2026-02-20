from __future__ import annotations

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

try:
    from multimodal_demo.application import load_action_catalog, load_demo_dataset
    from multimodal_demo.pipeline import PipelineInputs, run_operational_pipeline
except ModuleNotFoundError as exc:
    raise SystemExit("Package import failed. Run with `PYTHONPATH=src streamlit run app.py` or install with `pip install -e .`.") from exc

st.set_page_config(page_title="Multimodal Resilience Demo", layout="wide")
st.title("Multimodal Infrastructure Resilience Demo")
st.caption("Foundry-inspired architecture: Ontology -> Pipeline -> Operational App")

dataset = load_demo_dataset()
base_graph = dataset.to_graph(prefer_networkx=True)
actions = load_action_catalog()

st.sidebar.header("Pipeline Controls")
initial_failure = st.sidebar.multiselect("Initial failed assets", options=list(base_graph.nodes), default=["compressor_1"])
degradation_rate = st.sidebar.slider("Degradation rate", 0.05, 1.0, 0.35, 0.05)
threshold = st.sidebar.slider("Failure threshold", 0.0, 1.0, 0.4, 0.05)
max_steps = st.sidebar.slider("Simulation steps", 1, 12, 5)
coupling_mode = st.sidebar.selectbox("Interdependency logic", ["linear", "threshold"])
optimizer = st.sidebar.selectbox("Optimization method", ["greedy", "exact"])
budget = st.sidebar.slider("Response budget", 10, 300, 120)

result = run_operational_pipeline(
    dataset=dataset,
    actions_catalog=actions,
    inputs=PipelineInputs(
        failed_assets=initial_failure,
        degradation_rate=degradation_rate,
        dependency_threshold=threshold,
        max_steps=max_steps,
        coupling_mode=coupling_mode,
        optimization_strategy=optimizer,
        budget=budget,
    ),
)

left, right = st.columns((1, 1))
with left:
    st.subheader("Ontology Map")
    node_df = pd.DataFrame(
        [
            {
                "id": node,
                "name": data["name"],
                "domain": data["domain"],
                "lat": data["latitude"],
                "lon": data["longitude"],
                "condition": data.get("condition", 1.0),
            }
            for node, data in base_graph.nodes(data=True)
        ]
    )
    final_failed = {n for nodes in result.simulation_history.values() for n in nodes}
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
            tooltip={"text": "{name}\nDomain: {domain}\nCondition: {condition}"},
        )
    )

with right:
    st.subheader("Resilience Curves")
    curve_df = pd.DataFrame(result.resilience_points)
    st.plotly_chart(px.line(curve_df, x="step", y=["service_ratio", "health_index"], markers=True), use_container_width=True)
    st.metric("Final service ratio", f"{result.service_ratio:.2f}")
    st.metric("Final health index", f"{result.health_index:.2f}")

st.subheader("Decision Layer")
st.table(pd.DataFrame([a.__dict__ for a in result.selected_actions]))

with st.expander("Pipeline event log"):
    st.json(result.simulation_history)
