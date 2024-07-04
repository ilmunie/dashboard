import streamlit as st
from plotly.subplots import make_subplots
from frontend.visualization.candles import get_candlestick_trace
from frontend.visualization.signals import get_dca_mt_signal
from frontend.visualization.utils import add_traces_to_fig
from frontend.pages.config.utils import get_candles
from frontend.visualization import theme
from frontend.visualization.indicators import get_macd_traces_mt

from CONFIG import BACKEND_API_HOST, BACKEND_API_PORT
from backend.services.backend_api_client import BackendAPIClient
from frontend.components.backtesting import backtesting_section
from frontend.components.config_loader import get_default_config_loader
from frontend.components.dca_distribution import get_dca_distribution_inputs
from frontend.components.save_config import render_save_config
from frontend.pages.config.dca_macd_mt.user_inputs import user_inputs
from frontend.st_utils import initialize_st_page
from frontend.visualization.backtesting import create_backtesting_figure
from frontend.visualization.backtesting_metrics import render_backtesting_metrics, render_accuracy_metrics, \
    render_close_types
from frontend.visualization.dca_builder import create_dca_graph

# Initialize the Streamlit page
initialize_st_page(title="DCA MACD MULTI-TIMEFRAME", icon="🧙‍♂️")
backend_api_client = BackendAPIClient.get_instance(host=BACKEND_API_HOST, port=BACKEND_API_PORT)

# Page content
st.text("This tool will let you create a config for Bollinger DCA & MACD IN MULTI-TIMEFRAME and upload it to the BackendAPI.")
get_default_config_loader("macd_mt_dca")
inputs = user_inputs()

st.write("### Visualizing MACD MT and Trading Signals")
days_to_visualize = st.number_input("Days to Visualize", min_value=1, max_value=365, value=3)
## Load candle data
candles = get_candles(connector_name=inputs["candles_connector"], trading_pair=inputs["candles_trading_pair"], interval='1m', days=days_to_visualize)
## Create a subplot with 2 rows
fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                    vertical_spacing=0.02, subplot_titles=('Candlestick with SIGNALS', 'MACD (FAST MT)', 'MACD (SLOW MT)'),
                    row_heights=[0.8, 0.5, 0.5])
interval_durations = {
    '1s': 1,
    '1m': 60,
    '3m': 3 * 60,
    '5m': 5 * 60,
    '15m': 15 * 60,
    '30m': 30 * 60,
    '1h': 60 * 60,
    '4h': 4 * 60 * 60,
    '1d': 24 * 60 * 60,
}

macd_1_interval_seconds = interval_durations[inputs["macd_interval_1"]]
max_seconds_1 = max(macd_1_interval_seconds*(inputs["macd_slow_1"]+inputs['macd_signal_1'], days_to_visualize*24*3600))
days_to_visualize_macd_1 = max_seconds_1/(24*3600)
candles_macd_1 = get_candles(connector_name=inputs["candles_connector"], trading_pair=inputs["candles_trading_pair"], interval=inputs["macd_interval_1"], days=days_to_visualize_macd_1)

macd_2_interval_seconds = interval_durations[inputs["macd_interval_2"]]
max_seconds_2 = max(macd_2_interval_seconds*(inputs["macd_slow_2"]+inputs['macd_signal_2'], days_to_visualize*24*3600))
days_to_visualize_macd_2 = max_seconds_2/(24*3600)
candles_macd_2 = get_candles(connector_name=inputs["candles_connector"], trading_pair=inputs["candles_trading_pair"], interval=inputs["macd_interval_2"], days=days_to_visualize_macd_2)


add_traces_to_fig(fig, [get_candlestick_trace(candles)], row=1, col=1)
add_traces_to_fig(fig, get_dca_mt_signal(df=candles, macd_fast_1=inputs["macd_fast_1"], macd_slow_1=inputs["macd_slow_1"], macd_signal_1=inputs["macd_signal_1"], macd_signal_type_1=inputs["macd_signal_type_1"],
                                            macd_fast_2=inputs["macd_fast_2"],macd_slow_2=inputs["macd_slow_2"],macd_signal_2=inputs["macd_signal_2"],macd_signal_type_2=inputs["macd_signal_type_2"],
                                            macd_df_1=candles_macd_1, macd_df_2=candles_macd_2),
                  row=1, col=1)
add_traces_to_fig(fig, get_macd_traces_mt(df=candles, macd_fast=inputs["macd_fast_1"], macd_slow=inputs["macd_slow_1"],
                                          macd_signal=inputs["macd_signal_1"], macd_dataframe=candles_macd_1), row=2, col=1)
add_traces_to_fig(fig, get_macd_traces_mt(df=candles, macd_fast=inputs["macd_fast_2"], macd_slow=inputs["macd_slow_2"],
                                          macd_signal=inputs["macd_signal_2"], macd_dataframe=candles_macd_2), row=3, col=1)

#
fig.update_layout(**theme.get_default_layout())
## Use Streamlit's functionality to display the plot
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
#    config_base = st.text_input("Config Base", value=f"macd_bb_v1-{connector_name}-{trading_pair.split('-')[0]}")

render_save_config("macd_mt_dca", config)
