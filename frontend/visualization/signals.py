from frontend.visualization import theme
import plotly.graph_objects as go
import pandas_ta as ta  # noqa: F401
import pandas as pd


def get_dca_mt_signal(df, macd_fast_1, macd_slow_1,macd_signal_1, macd_signal_type_1,
                        macd_fast_2, macd_slow_2, macd_signal_2, macd_signal_type_2,
                        macd_df_1, macd_df_2):
    # Compute MACD for the first dataframe
    macd_df_1.ta.macd(fast=macd_fast_1, slow=macd_slow_1, signal=macd_signal_1, append=True)
    macd_1_col = f'MACD_{macd_fast_1}_{macd_slow_1}_{macd_signal_1}'
    macd_1_h_col = f'MACDh_{macd_fast_1}_{macd_slow_1}_{macd_signal_1}'

    macd_df_1['time'] = pd.to_datetime(macd_df_1['timestamp'], unit='s')
    macd_df_1["signal_macd_1"] = 0

    if macd_signal_type_1 == 'trend_following':
        long_condition_1 = (macd_df_1[macd_1_h_col] > 0)
        short_condition_1 = (macd_df_1[macd_1_h_col] < 0)
    else:
        long_condition_1 = (macd_df_1[macd_1_h_col] > 0) & (macd_df_1[macd_1_col] < 0)
        short_condition_1 = (macd_df_1[macd_1_h_col] < 0) & (macd_df_1[macd_1_col] > 0)

    macd_df_1.loc[long_condition_1, "signal_macd_1"] = 1
    macd_df_1.loc[short_condition_1, "signal_macd_1"] = -1

    # Compute MACD for the second dataframe
    macd_df_2.ta.macd(fast=macd_fast_2, slow=macd_slow_2, signal=macd_signal_2, append=True)
    macd_2_col = f'MACD_{macd_fast_2}_{macd_slow_2}_{macd_signal_2}'
    macd_2_h_col = f'MACDh_{macd_fast_2}_{macd_slow_2}_{macd_signal_2}'

    macd_df_2['time'] = pd.to_datetime(macd_df_2['timestamp'], unit='s')
    macd_df_2["signal_macd_2"] = 0

    if macd_signal_type_2 == 'trend_following':
        long_condition_2 = (macd_df_2[macd_2_h_col] > 0)
        short_condition_2 = (macd_df_2[macd_2_h_col] < 0)
    else:
        long_condition_2 = (macd_df_2[macd_2_h_col] > 0) & (macd_df_2[macd_2_col] < 0)
        short_condition_2 = (macd_df_2[macd_2_h_col] < 0) & (macd_df_2[macd_2_col] > 0)

    macd_df_2.loc[long_condition_2, "signal_macd_2"] = 1
    macd_df_2.loc[short_condition_2, "signal_macd_2"] = -1

    # Merge DataFrames on timestamp
    df['time'] = pd.to_datetime(df['timestamp'], unit='s')
    df = pd.merge_asof(df, macd_df_1[['time', 'signal_macd_1']], on='time', direction='backward')
    df = pd.merge_asof(df, macd_df_2[['time', 'signal_macd_2']], on='time', direction='backward')
    df.set_index('time', inplace=True)

    # Compute final signal
    df["signal"] = df.apply(
        lambda row: row['signal_macd_1'] if row['signal_macd_1'] == row['signal_macd_2'] else 0, axis=1)

    # Define buy and sell signals
    buy_signals = df[df['signal'] == 1]
    sell_signals = df[df['signal'] == -1]

    return get_signal_traces(buy_signals, sell_signals)

def get_bollinger_dca_mt_signal(df, bb_length, bb_std, bb_long_threshold, bb_short_threshold, macd_fast, macd_slow,
                                macd_signal, macd_signal_type, macd_df, bb_df):
    tech_colors = theme.get_color_scheme()
    df['time'] = pd.to_datetime(df['timestamp'], unit='s')
    bb_df.ta.bbands(length=bb_length, std=bb_std, append=True)
    bb_df['time'] = pd.to_datetime(bb_df['timestamp'], unit='s')
    bbp_col = f'BBP_{bb_length}_{bb_std}'

    macd_df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal, append=True)
    macd_col = f'MACD_{macd_fast}_{macd_slow}_{macd_signal}'
    macd_s_col = f'MACDs_{macd_fast}_{macd_slow}_{macd_signal}'
    macd_h_col = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal}'
    macd_df['time'] = pd.to_datetime(macd_df['timestamp'], unit='s')
    df['time'] = pd.to_datetime(df['timestamp'], unit='s')

    df = pd.merge_asof(df, macd_df[['time', macd_col, macd_s_col, macd_h_col]],
                       on='time',
                       direction='backward', )
    df = pd.merge_asof(df, bb_df[['time', bbp_col]],
                       on='time',
                       direction='backward', )
    df.set_index('time', inplace=True)
    bbp = df[bbp_col]
    macdh = df[macd_h_col]
    macd = df[macd_col]

    if macd_signal_type == 'trend_following':
        buy_signals = df[(bbp < bb_long_threshold) & (macdh > 0) & (macd < 0)]
        sell_signals = df[(bbp > bb_short_threshold) & (macdh < 0) & (macd > 0)]
    else:
        buy_signals = df[(bbp < bb_long_threshold) & (macdh > 0) & (macd < 0)]
        sell_signals = df[(bbp > bb_short_threshold) & (macdh < 0) & (macd > 0)]
    return get_signal_traces(buy_signals, sell_signals)



def get_signal_traces(buy_signals, sell_signals):
    tech_colors = theme.get_color_scheme()
    traces = [
        go.Scatter(x=buy_signals.index, y=buy_signals['close'], mode='markers',
                   marker=dict(color=tech_colors['buy_signal'], size=10, symbol='triangle-up'),
                   name='Buy Signal'),
        go.Scatter(x=sell_signals.index, y=sell_signals['close'], mode='markers',
                   marker=dict(color=tech_colors['sell_signal'], size=10, symbol='triangle-down'),
                   name='Sell Signal')
    ]
    return traces


def get_bollinger_v1_signal_traces(df, bb_length, bb_std, bb_long_threshold, bb_short_threshold):
    # Add Bollinger Bands
    candles = df.copy()
    candles.ta.bbands(length=bb_length, std=bb_std, append=True)

    # Generate conditions
    buy_signals = candles[candles[f"BBP_{bb_length}_{bb_std}"] < bb_long_threshold]
    sell_signals = candles[candles[f"BBP_{bb_length}_{bb_std}"] > bb_short_threshold]

    return get_signal_traces(buy_signals, sell_signals)


def get_macd_mean_reversion_signal_traces(df, macd_fast, macd_slow,macd_signal):
    tech_colors = theme.get_color_scheme()
    # Add Bollinger Bands
    # Add MACD
    df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal, append=True)
    # Decision Logic
    macdh = df[f"MACDh_{macd_fast}_{macd_slow}_{macd_signal}"]
    macd = df[f"MACD_{macd_fast}_{macd_slow}_{macd_signal}"]

    buy_signals = df[(macdh > 0) & (macd < 0)]
    sell_signals = df[(macdh < 0) & (macd > 0)]

    return get_signal_traces(buy_signals, sell_signals)


def get_macd_trend_following_signal_traces(df, macd_fast, macd_slow,macd_signal):
    tech_colors = theme.get_color_scheme()
    # Add Bollinger Bands
    # Add MACD
    df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal, append=True)
    # Decision Logic
    macdh = df[f"MACDh_{macd_fast}_{macd_slow}_{macd_signal}"]
    macd = df[f"MACD_{macd_fast}_{macd_slow}_{macd_signal}"]

    buy_signals = df[(macdh > 0) & (macd > 0)]
    sell_signals = df[(macdh < 0) & (macd < 0)]

    return get_signal_traces(buy_signals, sell_signals)

def get_macdbb_v1_signal_traces(df, bb_length, bb_std, bb_long_threshold, bb_short_threshold, macd_fast, macd_slow,
                                macd_signal):
    tech_colors = theme.get_color_scheme()
    # Add Bollinger Bands
    df.ta.bbands(length=bb_length, std=bb_std, append=True)
    # Add MACD
    df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal, append=True)
    # Decision Logic
    bbp = df[f"BBP_{bb_length}_{bb_std}"]
    macdh = df[f"MACDh_{macd_fast}_{macd_slow}_{macd_signal}"]
    macd = df[f"MACD_{macd_fast}_{macd_slow}_{macd_signal}"]

    buy_signals = df[(bbp < bb_long_threshold) & (macdh > 0) & (macd < 0)]
    sell_signals = df[(bbp > bb_short_threshold) & (macdh < 0) & (macd > 0)]

    return get_signal_traces(buy_signals, sell_signals)


def get_supertrend_v1_signal_traces(df, length, multiplier, percentage_threshold):
    # Add indicators
    df.ta.supertrend(length=length, multiplier=multiplier, append=True)
    df["percentage_distance"] = abs(df["close"] - df[f"SUPERT_{length}_{multiplier}"]) / df["close"]

    # Generate long and short conditions
    buy_signals = df[(df[f"SUPERTd_{length}_{multiplier}"] == 1) & (df["percentage_distance"] < percentage_threshold)]
    sell_signals = df[(df[f"SUPERTd_{length}_{multiplier}"] == -1) & (df["percentage_distance"] < percentage_threshold)]

    return get_signal_traces(buy_signals, sell_signals)
