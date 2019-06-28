import plotly as py
import plotly.graph_objs as go

def candlestick_chart(df, **kwargs):
    """" Dataframe column names must contain open, high, low and close """

    trace = go.Candlestick(open=df['open'], high=df['high'], low=df['low'], close=df['close'])

    y_axis = dict(range=[3000, 12000])

    # Create Layout
    layout = go.Layout(yaxis=y_axis)

    fig = go.Figure(data=[trace], layout=layout)

    py.offline.plot(fig)

