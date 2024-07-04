import streamlit as st
from frontend.components.market_making_general_inputs import get_market_making_general_inputs


def user_inputs():
    connector_name, trading_pair, leverage, total_amount_quote, position_mode, cooldown_time, executor_refresh_time, _, _, _ = get_market_making_general_inputs()

    #BBBANDS
    default_config = st.session_state.get("default_config", {})
    bb_length = default_config.get("bb_length", 100)
    bb_std = default_config.get("bb_std", 2.0)
    bb_long_threshold = default_config.get("bb_long_threshold", 0.0)
    bb_short_threshold = default_config.get("bb_short_threshold", 1.0)
    bb_interval = default_config.get("bb_interval", "3m")

    #MACD
    macd_fast = default_config.get("macd_fast", 21)
    macd_slow = default_config.get("macd_slow", 42)
    macd_signal = default_config.get("macd_signal", 9)
    macd_interval = default_config.get("macd_interval", "3m")
    macd_signal_type = default_config.get("macd_signal_type", "mean_reversion")


    max_executors_per_side = default_config.get("max_executors_per_side", 5)
    candles_connector_name = connector_name
    candles_trading_pair = trading_pair
    intervals = ["1m", "3m", "5m", "15m", "1h", "4h", "1d", "1s"]
    macd_signal_types = ["mean_reversion", "trend_following"]

    interval_index = intervals.index(bb_interval)

    with st.expander("Other Controller Settings", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            top_executor_refresh_time = st.number_input("Top Refresh Time (minutes)", value=60) * 60
        with c2:
            executor_activation_bounds = st.number_input("Activation Bounds (%)", value=0.1) / 100
            max_executors_per_side = st.number_input("Max Executors Per Side", value=max_executors_per_side,
                                                     help="Enter the maximum number of executors per side (e.g., 5).")

    with st.expander("Bollinger Bands Configuration", expanded=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            bb_length = st.number_input("Bollinger Bands Length", min_value=5, max_value=1000, value=bb_length)
        with c2:
            bb_std = st.number_input("Standard Deviation Multiplier", min_value=0.0, max_value=4.0, value=bb_std)
        with c3:
            bb_long_threshold = st.number_input("Long Threshold", value=bb_long_threshold)
        with c4:
            bb_short_threshold = st.number_input("Short Threshold", value=bb_short_threshold)
        with c5:
            bb_interval = st.selectbox("Candles Interval", ("1m", "3m", "5m", "15m", "1h", "4h", "1d"),
                                    index=interval_index,
                                    help="Enter the interval for candles (e.g., 1m).")

    interval_index = intervals.index(macd_interval)
    macd_signal_type_index = macd_signal_types.index(macd_signal_type)
    with st.expander("MACD Configuration", expanded=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            macd_fast = st.number_input("MACD Fast", min_value=1, value=macd_fast)
        with c2:
            macd_slow = st.number_input("MACD Slow", min_value=1, value=macd_slow)
        with c3:
            macd_signal = st.number_input("MACD Signal", min_value=1, value=macd_signal)
        with c4:
            macd_interval = st.selectbox("MACD Candles Interval", ("1m", "3m", "5m", "15m", "1h", "4h", "1d"),
                                    index=interval_index,
                                    help="Enter the interval for candles (e.g., 1m).")
        with c5:
            macd_signal_type = st.selectbox("MACD Signal type", options=["mean_reversion", "trend_following"],
                                            index=macd_signal_type_index)

    # Create the config
    config = {
        "controller_name": "bollinger_macd_dca",
        "controller_type": "directional_trading",
        "manual_kill_switch": None,
        "candles_config": [],
        "connector_name": connector_name,
        "trading_pair": trading_pair,
        "total_amount_quote": total_amount_quote,
        "candles_connector": candles_connector_name,
        "candles_trading_pair": candles_trading_pair,
        "macd_signal": macd_signal,
        "macd_slow": macd_slow,
        "macd_fast": macd_fast,
        "macd_interval": macd_interval,
        "macd_signal_type": macd_signal_type,
        "bb_interval": bb_interval,
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
