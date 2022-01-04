import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

import rapidhrv as rhv


def results_graph(analyzed, selected_column, selected_point=None):
    non_outlier = analyzed.loc[~analyzed["Outlier"]]
    outliers = analyzed.loc[analyzed["Outlier"]]

    fig = go.Figure(
        [
            go.Scatter(
                x=non_outlier["Time"],
                y=non_outlier[selected_column],
                name=selected_column,
                mode="lines+markers",
            ),
            go.Scatter(
                x=outliers["Time"],
                y=outliers[selected_column],
                name="Outliers",
                mode="markers",
            ),
        ]
    )

    if selected_point is not None:
        fig.add_trace(
            go.Scatter(x=[selected_point["x"]], y=[selected_point["y"]], showlegend=False)
        )
    fig.update_layout(template="plotly_white")

    return fig


def window_graph(window_data):
    signal, peaks, properties = window_data
    fig = go.Figure(
        [
            go.Scatter(y=signal),
            go.Scatter(
                x=peaks,
                y=properties["peak_heights"],
                mode="markers",
                marker=dict(line_color="darkorange", symbol="x-thin", size=24, line_width=1.5),
            ),
        ],
    )
    fig.update_layout(showlegend=False, template="plotly_white")

    return fig


def visualize(analyzed: pd.DataFrame, debug=False):
    app = dash.Dash()

    selected_column = "BPM"
    results = results_graph(analyzed, selected_column)

    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="column-dropdown",
                options=[{"label": col, "value": col} for col in rhv.analysis.DATA_COLUMNS],
                value=selected_column,
                clearable=False,
            ),
            dcc.Graph(id="results-graph", figure=results),
            html.Div(id="window-container"),
        ]
    )

    @app.callback(
        Output("results-graph", "figure"),
        Input("column-dropdown", "value"),
        Input("results-graph", "clickData"),
    )
    def update_results_graph(column, click_data):
        if click_data is None:
            return results_graph(analyzed, column)
        else:
            return results_graph(analyzed, column, selected_point=click_data["points"][0])

    @app.callback(Output("window-container", "children"), Input("results-graph", "clickData"))
    def update_window_graph(click_data):
        if click_data == None:
            return []

        selected_point = click_data["points"][0]
        window_data = analyzed.iloc[selected_point["pointNumber"]]["Window"]

        return [dcc.Graph(figure=window_graph(window_data))]

    app.run_server(debug=debug)


if __name__ == "__main__":
    signal = rhv.data.get_example_data()
    preprocessed = rhv.preprocess(signal)
    analyzed = rhv.analyze(preprocessed)
    visualize(analyzed, debug=True)
