import streamlit as st
from plotly.subplots import make_subplots
from frontend.visualization.candles import get_candlestick_trace
from frontend.visualization.indicators import get_bbands_traces, get_volume_trace
from frontend.visualization.signals import get_bollinger_v1_signal_traces
from frontend.visualization.utils import add_traces_to_fig
from frontend.pages.config.utils import get_candles
from frontend.visualization import theme

from CONFIG import BACKEND_API_HOST, BACKEND_API_PORT
from backend.services.backend_api_client import BackendAPIClient
from frontend.components.backtesting import backtesting_section
from frontend.components.config_loader import get_default_config_loader
from frontend.components.dca_distribution import get_dca_distribution_inputs
from frontend.components.save_config import render_save_config
from frontend.pages.config.bollinger_dca.user_inputs import user_inputs
from frontend.st_utils import initialize_st_page
from frontend.visualization.backtesting import create_backtesting_figure
from frontend.visualization.backtesting_metrics import render_backtesting_metrics, render_accuracy_metrics, \
    render_close_types
from frontend.visualization.dca_builder import create_dca_graph
from frontend.visualization.executors_distribution import create_executors_distribution_traces

# Initialize the Streamlit page
initialize_st_page(title="Bollinger DCA", icon="🧙‍♂️")
backend_api_client = BackendAPIClient.get_instance(host=BACKEND_API_HOST, port=BACKEND_API_PORT)

# Page content
st.text("This tool will let you create a config for Bollinger DCA and upload it to the BackendAPI.")
get_default_config_loader("bollinger_dca")
inputs = user_inputs()
st.write("### Visualizing Bollinger Bands and Trading Signals")
days_to_visualize = st.number_input("Days to Visualize", min_value=1, max_value=365, value=3)
# Load candle data
candles = get_candles(connector_name=inputs["candles_connector"], trading_pair=inputs["candles_trading_pair"], interval=inputs["interval"], days=days_to_visualize)
# Create a subplot with 2 rows
fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0.02, subplot_titles=('Candlestick with Bollinger Bands', 'Volume'),
                    row_heights=[0.8, 0.2])

add_traces_to_fig(fig, [get_candlestick_trace(candles)], row=1, col=1)
add_traces_to_fig(fig, get_bbands_traces(candles, inputs["bb_length"], inputs["bb_std"]), row=1, col=1)
add_traces_to_fig(fig, get_bollinger_v1_signal_traces(candles, inputs["bb_length"], inputs["bb_std"], inputs["bb_long_threshold"], inputs["bb_short_threshold"]), row=1, col=1)
add_traces_to_fig(fig, [get_volume_trace(candles)], row=2, col=1)
fig.update_layout(**theme.get_default_layout())
# Use Streamlit's functionality to display the plot
st.plotly_chart(fig, use_container_width=True)

# DCA CONFIG
dca_inputs = get_dca_distribution_inputs()
st.write("### Visualizing DCA Distribution")
st.write("---")
fig = create_dca_graph(dca_inputs, inputs["total_amount_quote"])
st.plotly_chart(fig, use_container_width=True)

# Combine inputs and dca_inputs into final config
config = {**inputs, **dca_inputs}

st.session_state["default_config"] = config
config.pop('candles_config')
config.pop('candles_trading_pair')
config.pop('top_executor_refresh_time')
bt_results = backtesting_section(config, backend_api_client)
if bt_results:
    fig = create_backtesting_figure(
        df=bt_results["processed_data"],
        executors=bt_results["executors"],
        config=inputs)
    c1, c2 = st.columns([0.9, 0.1])
    with c1:
        render_backtesting_metrics(bt_results["results"])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        render_accuracy_metrics(bt_results["results"])
        st.write("---")
        render_close_types(bt_results["results"])
st.write("---")
render_save_config("bollinger_dca", config)
