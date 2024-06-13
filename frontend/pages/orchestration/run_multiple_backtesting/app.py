from types import SimpleNamespace

import streamlit as st
from streamlit_elements import elements, mui

from frontend.components.dashboard import Dashboard
from frontend.components.backtest_multiple_config import RunMultipleBacktesting
from frontend.st_utils import initialize_st_page

CARD_WIDTH = 6
CARD_HEIGHT = 3
NUM_CARD_COLS = 2

initialize_st_page(title="Multiple Backtesting", icon="🙌")

if "run_multiple_backtesting" not in st.session_state:
    board = Dashboard()
    run_multiple_backtesting = SimpleNamespace(
        dashboard=board,
        run_multiple_backtesting=RunMultipleBacktesting(board, 0, 0, 12, 10),

    )
    st.session_state.run_multiple_backtesting = run_multiple_backtesting

else:
    run_multiple_backtesting = st.session_state.run_multiple_backtesting


with elements("create_bot"):
    with mui.Paper(elevation=3, style={"padding": "2rem"}, spacing=[2, 2], container=True):
        with run_multiple_backtesting.dashboard():
            run_multiple_backtesting.run_multiple_backtesting()
