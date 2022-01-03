import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from plotly import subplots

import rapidhrv as rhv

DATA_COLUMNS = [col for col in rhv.analysis.DATAFRAME_COLUMNS if col not in {"Time", "Outlier"}]
AXES = {"BPM": 1, "RMSSD": 2, "SDNN": 2, "SDSD": 2, "pNN20": 3, "pNN50": 3, "HF": 4}


def plot_data(data: pd.DataFrame):

    fig = subplots.make_subplots(
        rows=len(set(AXES.values())),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        x_title="Time",
    )

    fig.add_traces(
        [
            go.Scatter(
                x=data["Time"],
                y=data[col],
                mode="markers",
                marker=dict(
                    symbol=data["Outlier"].map({False: "circle", True: "x"}),
                    opacity=data["Outlier"].map({False: 1.0, True: 0.2}),
                ),
                name=col,
            )
            for col in DATA_COLUMNS
        ],
        rows=[AXES[col] for col in DATA_COLUMNS],
        cols=1,
    )

    fig.update_layout(
        height=700,
        hovermode="closest",
        clickmode="event+select",
    )

    return fig


def plot_signal(signal: rhv.Signal):
    pass


def create_app():
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.H1("Rapid HRV"),
            html.Div(
                [
                    html.Div(
                        [
                            "Analysis results: ",
                            dcc.Input(id="analysis-input", value="analyzed.csv"),
                            "Signal: ",
                            dcc.Input(id="signal-input", value="resources/signal.hdf5"),
                        ]
                    ),
                ]
            ),
            dcc.Graph(
                id="analysis-graph",
                figure=plot_data(pd.DataFrame(columns=rhv.analysis.DATAFRAME_COLUMNS)),
            ),
            dcc.Graph(
                id="signal-graph",
                figure=plot_data(pd.DataFrame(columns=rhv.analysis.DATAFRAME_COLUMNS)),
            ),
        ],
        style={"font-family": "sans-serif"},
    )

    @app.callback(
        Output(component_id="analysis-graph", component_property="figure"),
        Input(component_id="analysis-input", component_property="value"),
    )
    def update_analysis(filename):
        try:
            return plot_data(pd.read_csv(filename))
        except FileNotFoundError:
            return plot_data(pd.DataFrame(columns=rhv.analysis.DATAFRAME_COLUMNS))

    @app.callback(
        Output(component_id="signal-graph", component_property="figure"),
        Input(component_id="signal-input", component_property="value"),
    )
    def load_signal(filename):
        try:
            return plot_data(pd.read_csv(filename))
        except FileNotFoundError:
            return plot_data(pd.DataFrame(columns=rhv.analysis.DATAFRAME_COLUMNS))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True)
