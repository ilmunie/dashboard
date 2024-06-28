import streamlit as st
from frontend.components.market_making_general_inputs import get_market_making_general_inputs


def user_inputs():
    connector_name, trading_pair, leverage, total_amount_quote, position_mode, cooldown_time, executor_refresh_time, _, _, _ = get_market_making_general_inputs()

    default_config = st.session_state.get("default_config", {})
    macd_fast = default_config.get("macd_fast", 21)
    macd_slow = default_config.get("macd_slow", 42)
    macd_signal = default_config.get("macd_signal", 9)
    max_executors_per_side = default_config.get("max_executors_per_side", 5)
    max_executors_per_side = default_config.get("max_executors_per_side", 5)

    candles_connector_name = connector_name
    candles_trading_pair = trading_pair
    interval = default_config.get("interval", "3m")
    intervals = ["1m", "3m", "5m", "15m", "1h", "4h", "1d", "1s"]
    interval_index = intervals.index(interval)

    with st.expander("Custom DCA Settings", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            top_executor_refresh_time = st.number_input("Top Refresh Time (minutes)", value=60) * 60
        with c2:
            executor_activation_bounds = st.number_input("Activation Bounds (%)", value=0.1) / 100
            max_executors_per_side = st.number_input("Max Executors Per Side", value=max_executors_per_side,
                                                     help="Enter the maximum number of executors per side (e.g., 5).")

    with st.expander("MACD Configuration", expanded=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            macd_fast = st.number_input("MACD Fast", min_value=1, value=macd_fast)
        with c2:
            macd_slow = st.number_input("MACD Slow", min_value=1, value=macd_slow)
        with c3:
            macd_signal = st.number_input("MACD Signal", min_value=1, value=macd_signal)
        with c4:
            interval = st.selectbox("Interval", options=["1m", "3m", "5m", "15m", "1h", "4h", "1d", "1s"])
        with c5:
            macd_signal_type = st.selectbox("MACD Signal type", options=["mean_reversion", "trend_following"])

    # Create the config
    config = {
        "controller_name": "macd_dca_v1",
        "controller_type": "directional_trading",
        "manual_kill_switch": None,
        "candles_config": [],
        "connector_name": connector_name,
        "trading_pair": trading_pair,
        "total_amount_quote": total_amount_quote,
        "candles_connector": candles_connector_name,
        "macd_signal_type": macd_signal_type,
        "candles_trading_pair": candles_trading_pair,
        "interval": interval,
        "macd_fast": macd_fast,
        "macd_slow": macd_slow,
        "max_executors_per_side": max_executors_per_side,
        "macd_signal": macd_signal,
        "executor_refresh_time": executor_refresh_time,
        "cooldown_time": cooldown_time,
        "leverage": leverage,
        "position_mode": position_mode,
        "top_executor_refresh_time": top_executor_refresh_time,
        "executor_activation_bounds": [executor_activation_bounds]
    }

    return config
