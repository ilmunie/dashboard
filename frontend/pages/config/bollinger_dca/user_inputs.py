import streamlit as st

from frontend.components.executors_distribution import get_executors_distribution_inputs
from frontend.components.market_making_general_inputs import get_market_making_general_inputs


def user_inputs():
    connector_name, trading_pair, leverage, total_amount_quote, position_mode, cooldown_time, executor_refresh_time, _, _, _ = get_market_making_general_inputs()

    #BBBANDS
    default_config = st.session_state.get("default_config", {})
    bb_length = default_config.get("bb_length", 100)
    bb_std = default_config.get("bb_std", 2.0)
    bb_long_threshold = default_config.get("bb_long_threshold", 0.0)
    bb_short_threshold = default_config.get("bb_short_threshold", 1.0)
    max_executors_per_side = default_config.get("max_executors_per_side", 5)
    candles_connector_name = connector_name
    candles_trading_pair = trading_pair
    interval = default_config.get("interval", "3m")
    intervals = ["1m", "3m", "5m", "15m", "1h", "4h", "1d", "1s"]
    interval_index = intervals.index(interval)

    with st.expander("Custom Bollinger DCA Settings", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            top_executor_refresh_time = st.number_input("Top Refresh Time (minutes)", value=60) * 60
        with c2:
            executor_activation_bounds = st.number_input("Activation Bounds (%)", value=0.1) / 100
            max_executors_per_side = st.number_input("Max Executors Per Side", value=max_executors_per_side,
                                                     help="Enter the maximum number of executors per side (e.g., 5).")

    with st.expander("Bollinger Bands Configuration", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            bb_length = st.number_input("Bollinger Bands Length", min_value=5, max_value=1000, value=bb_length)
        with c2:
            bb_std = st.number_input("Standard Deviation Multiplier", min_value=0.0, max_value=4.0, value=bb_std)
        with c3:
            bb_long_threshold = st.number_input("Long Threshold", value=bb_long_threshold)
        with c4:
            bb_short_threshold = st.number_input("Short Threshold", value=bb_short_threshold)
            interval = st.selectbox("Candles Interval", ("1m", "3m", "5m", "15m", "1h", "4h", "1d"),
                                    index=interval_index,
                                    help="Enter the interval for candles (e.g., 1m).")

    # Create the config
    config = {
        "controller_name": "bollinger_dca",
        "controller_type": "directional_trading",
        "manual_kill_switch": None,
        "candles_config": [],
        "connector_name": connector_name,
        "trading_pair": trading_pair,
        "total_amount_quote": total_amount_quote,
        "candles_connector": candles_connector_name,
        "candles_trading_pair": candles_trading_pair,
        "interval": interval,
        "bb_length": bb_length,
        "bb_std": bb_std,
        "max_executors_per_side": max_executors_per_side,
        "bb_long_threshold": bb_long_threshold,
        "bb_short_threshold": bb_short_threshold,
        "executor_refresh_time": executor_refresh_time,
        "cooldown_time": cooldown_time,
        "leverage": leverage,
        "position_mode": position_mode,
        "top_executor_refresh_time": top_executor_refresh_time,
        "executor_activation_bounds": [executor_activation_bounds]
    }

    return config
