import time

import streamlit as st
from streamlit_elements import mui, lazy
from datetime import datetime, timedelta
from frontend.visualization.backtesting import create_backtesting_figure
from frontend.visualization.backtesting_metrics import render_backtesting_metrics, render_accuracy_metrics, \
    render_close_types
DEFAULT_ROWS = []
from CONFIG import BACKEND_API_HOST, BACKEND_API_PORT
from backend.services.backend_api_client import BackendAPIClient
from .dashboard import Dashboard
import json

backend_api_client = BackendAPIClient.get_instance(host=BACKEND_API_HOST, port=BACKEND_API_PORT)


class RunMultipleBacktesting(Dashboard.Item):
    DEFAULT_COLUMNS = [
        {"field": 'id', "headerName": 'ID', "width": 400},
        {"field": 'controller_name', "headerName": 'Controller Name', "width": 150, "editable": False, },
        {"field": 'controller_type', "headerName": 'Controller Type', "width": 150, "editable": False, },
        {"field": 'connector_name', "headerName": 'Connector', "width": 150, "editable": False, },
        {"field": 'trading_pair', "headerName": 'Trading pair', "width": 140, "editable": False, },
        {"field": 'total_amount_quote', "headerName": 'Total amount ($)', "width": 140, "editable": False, },
        {"field": 'max_loss_quote', "headerName": 'Max loss ($)', "width": 120, "editable": False, },
        {"field": 'stop_loss', "headerName": 'SL (%)', "width": 100, "editable": False, },
        {"field": 'take_profit', "headerName": 'TP (%)', "width": 100, "editable": False, },
        {"field": 'trailing_stop', "headerName": 'TS (%)', "width": 120, "editable": False, },
        {"field": 'time_limit', "headerName": 'Time limit', "width": 100, "editable": False, },
    ]
    DEFAULT_RESULT_COLUMNS = [
        {"field": 'id', "headerName": 'ID', "width": 400},
        {"field": 'net_pnl', "headerName": 'net_pnl', "width": 100, "editable": False, },
        {"field": 'net_pnl_quote', "headerName": 'net_pnl_quote', "width": 100, "editable": False, },
        {"field": 'total_executors', "headerName": 'total_executors', "width": 100, "editable": False, },
        {"field": 'total_executors_with_position', "headerName": 'total_executors_with_position', "width": 100,
         "editable": False, },
        {"field": 'total_volume', "headerName": 'total_volume', "width": 100, "editable": False, },
        {"field": 'total_long', "headerName": 'total_long', "width": 100, "editable": False, },
        {"field": 'total_short', "headerName": 'total_short', "width": 100, "editable": False, },
        {"field": 'close_types', "headerName": 'close_types', "width": 100, "editable": False, },
        {"field": 'accuracy_long', "headerName": 'accuracy_long', "width": 100, "editable": False, },
        {"field": 'accuracy_short', "headerName": 'accuracy_short', "width": 100, "editable": False, },
        {"field": 'total_positions', "headerName": 'total_positions', "width": 100, "editable": False, },
        {"field": 'accuracy', "headerName": 'accuracy', "width": 100, "editable": False, },
        {"field": 'max_drawdown_usd', "headerName": 'max_drawdown_usd', "width": 100, "editable": False, },
        {"field": 'max_drawdown_pct', "headerName": 'max_drawdown_pct', "width": 100, "editable": False, },
        {"field": 'sharpe_ratio', "headerName": 'sharpe_ratio', "width": 100, "editable": False, },
        {"field": 'profit_factor', "headerName": 'profit_factor', "width": 100, "editable": False, },
        {"field": 'win_signals', "headerName": 'win_signals', "width": 100, "editable": False, },
        {"field": 'loss_signals', "headerName": 'loss_signals', "width": 100, "editable": False, },

    ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backend_api_client = BackendAPIClient.get_instance(host=BACKEND_API_HOST, port=BACKEND_API_PORT)
        self._controller_configs_available = self._backend_api_client.get_all_controllers_config()
        self._controller_config_selected = None
        self._result_config_selected = None
        self._start_date = None
        self._end_date = None
        self._time_resolution = None
        self._trade_cost = None
        self._backtesting_results = []
        self._bot_name = None
        self._image_name = "dardonacci/hummingbot:latest"
        self._credentials = "master_account"
        self._cash_out_time = None
        self._max_portfolio_loss = None

    def _set_bot_name(self, event):
        self._bot_name = event.target.value

    def _set_image_name(self, _, childs):
        self._image_name = childs.props.value

    def _set_credentials(self, _, childs):
        self._credentials = childs.props.value

    def _set_cash_out_time(self, event):
        self._cash_out_time = float(event.target.value)

    def _set_max_portfolio_loss(self, event):
        self._max_portfolio_loss = float(event.target.value)
    def _set_backtesting_resolution(self, event):
        self._backtesting_resolution = event.target.value

    def _set_controller(self, event):
        self._controller_selected = event.target.value
    def _handle_config_selected(self, params, _):
        self._result_config_selected = [param + "" for param in params]
    def _handle_row_selection(self, params, _):
        self._controller_config_selected = [param + "" for param in params]
    def run_backtestings(self):
            results = []
            if not self._controller_config_selected:
                st.error("No configs selected!")
                return None
            all_controllers = self._backend_api_client.get_all_controllers_config()
            selected_controllers = [controller for controller in all_controllers if
                                    controller['id'] in self._controller_config_selected]
            start_datetime = datetime.combine(self._start_date, datetime.min.time())
            end_datetime = datetime.combine(self._end_date, datetime.max.time())
            for controller in selected_controllers:
                results.append((controller, self._backend_api_client.run_backtesting(
                start_time=int(start_datetime.timestamp()) * 1000,
                end_time=int(end_datetime.timestamp()) * 1000,
                backtesting_resolution=self._time_resolution,
                trade_cost=self._trade_cost / 100,
                config=controller,)))
            self._backtesting_results = results
            with st.spinner('Starting Backtesting... This process may take a few seconds'):
                time.sleep(3)

    def launch_new_bot(self):
        if self._bot_name and self._image_name and len(self._controller_config_selected) > 0:
            start_time_str = time.strftime("%Y.%m.%d_%H.%M")
            bot_name = f"{self._bot_name}-{start_time_str}"
            script_config = {
                "name": bot_name,
                "content": {
                    "markets": {},
                    "candles_config": [],
                    "controllers_config": [name_id + ".yml" for name_id in self._result_config_selected],
                    "config_update_interval": 10,
                    "script_file_name": "v2_with_controllers.py",
                    "time_to_cash_out": self._cash_out_time,
                    "max_portfolio_loss": self._max_portfolio_loss,
                }
            }
            self._backend_api_client.add_script_config(script_config)
            deploy_config = {
                "instance_name": bot_name,
                "script": "v2_with_controllers.py",
                "script_config": bot_name + ".yml",
                "image": self._image_name,
                "credentials_profile": self._credentials,
                "time_to_cash_out": self._cash_out_time,
                "max_portfolio_loss": self._max_portfolio_loss,
            }
            self._backend_api_client.create_hummingbot_instance(deploy_config)
            with st.spinner('Starting Bot... This process may take a few seconds'):
                time.sleep(3)
        else:
            st.warning("You need to define the bot name and select the controllers configs "
                       "that you want to deploy.")



    def __call__(self):

        st.write("### Backtesting")
        c1, c2, c3, c4 = st.columns(4)
        default_end_time = datetime.now().date() - timedelta(days=1)
        default_start_time = default_end_time - timedelta(days=2)
        disabled = True if self._backtesting_results else False
        with c1:
            self._start_date = st.date_input("Start Date", default_start_time, disabled=disabled)
        with c2:
            self._end_date = st.date_input("End Date", default_end_time, disabled=disabled,
                                     help="End date is inclusive, make sure that you are not including the current date.")
        with c3:
            self._time_resolution = st.selectbox("Backtesting Resolution", disabled=disabled,
                                                  options=["1m", "3m", "5m", "15m", "30m", "1h", "1s"], index=0)
        with c4:
            self._trade_cost = st.number_input("Trade Cost (%)", min_value=0.0, disabled=disabled, value=0.06, step=0.01, format="%.2f")
        if not self._backtesting_results:
            with mui.Paper(key=self._key,
                           sx={"display": "flex", "flexDirection": "column", "borderRadius": 3, "overflow": "hidden"},
                           elevation=1 ):
                with self.title_bar(padding="10px 15px 10px 15px", dark_switcher=False):
                    mui.Typography("🚀 Select the controller configs to backtest", variant="h5")
                with mui.Grid(container=True, spacing=2, sx={"padding": "10px 15px 10px 15px"}):
                    with mui.Grid(item=True, xs=8):
                        mui.Alert(
                            "Select the controllers to backtest",
                            severity="info")
                    with mui.Grid(item=True, xs=4):
                        with mui.Button(onClick=self.run_backtestings,
                                        variant="outlined",
                                        color="success",
                                        sx={"width": "100%", "height": "100%"}):
                            mui.icon.AddCircleOutline()
                            mui.Typography("Run")
                    all_controllers_config = self._backend_api_client.get_all_controllers_config()
                    data = []
                    for config in all_controllers_config:
                        connector_name = config.get("connector_name", "Unknown")
                        trading_pair = config.get("trading_pair", "Unknown")
                        total_amount_quote = config.get("total_amount_quote", 0)
                        stop_loss = config.get("stop_loss", 0)
                        take_profit = config.get("take_profit", 0)
                        trailing_stop = config.get("trailing_stop", {"activation_price": 0, "trailing_delta": 0})
                        time_limit = config.get("time_limit", 0)
                        data.append({"id": config["id"], "controller_name": config["controller_name"],
                                     "controller_type": config["controller_type"],
                                     "connector_name": connector_name,
                                     "trading_pair": trading_pair,
                                     "total_amount_quote": total_amount_quote,
                                     "max_loss_quote": total_amount_quote * stop_loss / 2,
                                     "stop_loss": stop_loss,
                                     "take_profit": take_profit,
                                     "trailing_stop": str(trailing_stop["activation_price"]) + " / " +
                                                      str(trailing_stop["trailing_delta"]),
                                     "time_limit": time_limit})
                    with mui.Grid(item=True, xs=12):
                        with mui.Paper(key=self._key,
                                       sx={"display": "flex", "flexDirection": "column", "borderRadius": 3,
                                           "overflow": "hidden", "height": 1000},
                                       elevation=1):
                            with mui.Box(sx={"flex": 1, "minHeight": 3}):
                                mui.DataGrid(
                                    columns=self.DEFAULT_COLUMNS,
                                    rows=data,
                                    pageSize=15,
                                    rowsPerPageOptions=[15],
                                    checkboxSelection=True,
                                    disableSelectionOnClick=True,
                                    onSelectionModelChange=self._handle_row_selection,
                                )
        if self._backtesting_results:
            data = []
            for tuple in self._backtesting_results:
                config = tuple[0]
                result = tuple[1]
                data.append(result["results"] | {'id': config['id']})
            with mui.Paper(key=self._key,
                           sx={"display": "flex", "flexDirection": "column", "borderRadius": 3, "overflow": "hidden"},
                           elevation=1):
                with self.title_bar(padding="10px 15px 10px 15px", dark_switcher=False):
                    mui.Typography("🚀 Select the controller configs to launch", variant="h5")

                with mui.Grid(container=True, spacing=2, sx={"padding": "10px 15px 10px 15px"}):
                    with mui.Grid(item=True, xs=8):
                        mui.Alert(
                            "The new instance will contain the credentials configured in the following base instance:",
                            severity="info")
                    with mui.Grid(item=True, xs=4):
                        available_credentials = self._backend_api_client.get_accounts()
                        with mui.FormControl(variant="standard", sx={"width": "100%"}):
                            mui.FormHelperText("Credentials")
                            with mui.Select(label="Credentials", defaultValue="master_account",
                                            variant="standard", onChange=lazy(self._set_credentials)):
                                for master_config in available_credentials:
                                    mui.MenuItem(master_config, value=master_config)
                    with mui.Grid(item=True, xs=4):
                        mui.TextField(label="Instance Name", variant="outlined", onChange=lazy(self._set_bot_name),
                                      sx={"width": "100%"})
                    with mui.Grid(item=True, xs=8):
                        available_images = self._backend_api_client.get_available_images("hummingbot")
                        with mui.FormControl(variant="standard", sx={"width": "100%"}):
                            mui.FormHelperText("Available Images")
                            with mui.Select(label="Hummingbot Image", defaultValue="dardonacci/hummingbot:latest",
                                            variant="standard", onChange=lazy(self._set_image_name)):
                                for image in available_images:
                                    mui.MenuItem(image, value=image)
                    with mui.Grid(item=True, xs=4):
                        mui.TextField(label="Time to Cash-out (s)", variant="outlined",
                                      onChange=lazy(self._set_cash_out_time),
                                      sx={"width": "100%"})
                    with mui.Grid(item=True, xs=4):
                        mui.TextField(label="Max portfolio-loss (quote assets)", variant="outlined",
                                      onChange=lazy(self._set_max_portfolio_loss),
                                      sx={"width": "100%"})
                    with mui.Grid(item=True, xs=4):
                        with mui.Button(onClick=self.launch_new_bot,
                                        variant="outlined",
                                        color="success",
                                        sx={"width": "100%", "height": "100%"}):
                            mui.icon.AddCircleOutline()
                            mui.Typography("Deploy")

                #with mui.Grid(container=True, spacing=2, sx={"padding": "10px 15px 10px 15px"}):
                    with mui.Grid(item=True, xs=12):
                        mui.Alert("Select a backtesting to analyse and deploy", severity="info")
                        with mui.Paper(key=self._key,
                                       sx={"display": "flex", "flexDirection": "column", "borderRadius": 3,
                                           "overflow": "hidden", "height": 1000},
                                       elevation=1):
                            with mui.Box(sx={"flex": 1, "minHeight": 3}):
                                mui.DataGrid(
                                    columns=self.DEFAULT_RESULT_COLUMNS,
                                    rows=data,
                                    pageSize=15,
                                    rowsPerPageOptions=[15],
                                    checkboxSelection=True,
                                    disableSelectionOnClick=True,
                                    onSelectionModelChange=self._handle_config_selected,
                                )
        if self._result_config_selected:
            for result_id in self._result_config_selected:
                tuple = next(filter(lambda tup: tup[0]['id'] == result_id, self._backtesting_results), None)
                fig = create_backtesting_figure(
                    df=tuple[1]["processed_data"],
                    executors=tuple[1]["executors"],
                    config=tuple[0])
                with st.expander("Backtesting Result |" + tuple[0]['id'], expanded=False):
                    c1, c2 = st.columns([0.9, 0.1])
                    with c1:
                        render_backtesting_metrics(tuple[1]["results"])
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        render_accuracy_metrics(tuple[1]["results"])
                        st.write("---")
                        render_close_types(tuple[1]["results"])

