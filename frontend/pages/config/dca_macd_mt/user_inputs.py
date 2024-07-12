import streamlit as st
from frontend.components.market_making_general_inputs import get_market_making_general_inputs


def user_inputs():
    connector_name, trading_pair, leverage, total_amount_quote, position_mode, cooldown_time, executor_refresh_time, _, _, _ = get_market_making_general_inputs()

    default_config = st.session_state.get("default_config", {})
    #MACD
    macd_fast_1 = default_config.get("macd_fast_1", 21)
    macd_slow_1 = default_config.get("macd_slow_1", 42)
    macd_signal_1 = default_config.get("macd_signal_1", 9)
    macd_interval_1 = default_config.get("macd_interval_1", "3m")
    macd_signal_type_1 = default_config.get("macd_signal_type_1", "mean_reversion_1")
    #MACD
    macd_fast_2 = default_config.get("macd_fast_2", 21)
    macd_slow_2 = default_config.get("macd_slow_2", 42)
    macd_signal_2 = default_config.get("macd_signal_2", 9)
    macd_interval_2 = default_config.get("macd_interval_2", "3m")
    macd_signal_type_2 = default_config.get("macd_signal_type_2", "mean_reversion_1")
    max_executors_per_side = default_config.get("max_executors_per_side", 5)
    macd_number_of_candles_1 = default_config.get("macd_number_of_candles_1", 4)
    macd_number_of_candles_2 = default_config.get("macd_number_of_candles_2", 4)
    candles_connector_name = connector_name
    candles_trading_pair = trading_pair
    #selection fields
    intervals = ["1m", "3m", "5m", "15m", "1h", "4h", "1d", "1s"]
    interval_index_1 = intervals.index(macd_interval_1)
    interval_index_2 = intervals.index(macd_interval_2)

    macd_signal_types = ["mean_reversion_1","mean_reversion_2", "trend_following"]
    macd_1_signal_type_index = macd_signal_types.index(macd_signal_type_1)
    macd_2_signal_type_index = macd_signal_types.index(macd_signal_type_2)

    with st.expander("Other Controller Settings", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            top_executor_refresh_time = st.number_input("Top Refresh Time (minutes)", value=60) * 60
        with c2:
            executor_activation_bounds = st.number_input("Activation Bounds (%)", value=0.1) / 100
            max_executors_per_side = st.number_input("Max Executors Per Side", value=max_executors_per_side,
                                                     help="Enter the maximum number of executors per side (e.g., 5).")

    with st.expander("MACD FAST Configuration", expanded=True):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            macd_fast_1 = st.number_input("MACD Fast", min_value=1, value=macd_fast_1)
        with c2:
            macd_slow_1 = st.number_input("MACD Slow", min_value=1, value=macd_slow_1)
        with c3:
            macd_signal_1 = st.number_input("MACD Signal", min_value=1, value=macd_signal_1)
        with c4:
            macd_interval_1 = st.selectbox("MACD Candles Interval", ("1m", "3m", "5m", "15m", "1h", "4h", "1d"),
                                    index=interval_index_1,
                                    help="Enter the interval for candles (e.g., 1m).")
        with c5:
            macd_signal_type_1 = st.selectbox("MACD Signal type", options=["mean_reversion_1","mean_reversion_2", "trend_following"],
                                              index=macd_1_signal_type_index)
        with c6:
            macd_number_of_candles_1 = st.number_input("Number of Candles 1", min_value=2, value=macd_number_of_candles_1)
    with st.expander("MACD SLOW Configuration", expanded=True):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            macd_fast_2 = st.number_input("MACD 2", min_value=1, value=macd_fast_2)
        with c2:
            macd_slow_2 = st.number_input("MACD Slow 2", min_value=1, value=macd_slow_2)
        with c3:
            macd_signal_2 = st.number_input("MACD Signal 2", min_value=1, value=macd_signal_2)
        with c4:
            macd_interval_2 = st.selectbox("MACD 2 Candles Interval", ("1m", "3m", "5m", "15m", "1h", "4h", "1d"),
                                    index=interval_index_2,
                                    help="Enter the interval for candles (e.g., 1m).")
        with c5:
            macd_signal_type_2 = st.selectbox("MACD 2 Signal type", options=["mean_reversion_1","mean_reversion_2", "trend_following"],
                                              index=macd_2_signal_type_index)
        with c6:
            macd_number_of_candles_2 = st.number_input("Number of Candles 2", min_value=2, value=macd_number_of_candles_2)

    # Create the config
    config = {
        "controller_name": "macd_mt_dca",
        "controller_type": "directional_trading",
        "manual_kill_switch": None,
        "candles_config": [],
        "connector_name": connector_name,
        "trading_pair": trading_pair,
        "total_amount_quote": total_amount_quote,
        "candles_connector": candles_connector_name,
        "candles_trading_pair": candles_trading_pair,
        "macd_signal_1": macd_signal_1,
        "macd_slow_1": macd_slow_1,
        "macd_fast_1": macd_fast_1,
        "macd_interval_1": macd_interval_1,
        "macd_signal_type_1": macd_signal_type_1,
        "macd_number_of_candles_1": macd_number_of_candles_1,
        "macd_signal_2": macd_signal_2,
        "macd_slow_2": macd_slow_2,
        "macd_fast_2": macd_fast_2,
        "macd_interval_2": macd_interval_2,
        "macd_signal_type_2": macd_signal_type_2,
        "macd_number_of_candles_2": macd_number_of_candles_2,
        "max_executors_per_side": max_executors_per_side,
        "executor_refresh_time": executor_refresh_time,
        "cooldown_time": cooldown_time,
        "leverage": leverage,
        "position_mode": position_mode,
        "top_executor_refresh_time": top_executor_refresh_time,
        "executor_activation_bounds": [executor_activation_bounds]
    }

    return config
