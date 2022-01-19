import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

import rapidhrv as rhv


def results_graph(non_outliers, outliers, selected_column):
    fig = go.Figure(
        [
            go.Scatter(
                x=non_outliers["Time"],
                y=non_outliers[selected_column],
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

    fig.update_layout(template="plotly_white", clickmode="event+select")
    fig.update_traces(marker_size=10)

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

    non_outlier_data = analyzed.loc[~analyzed["Outlier"]]
    outlier_data = analyzed.loc[analyzed["Outlier"]]

    selected_column = "BPM"
    results = results_graph(non_outlier_data, outlier_data, selected_column)

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

    @app.callback(Output("results-graph", "figure"), Input("column-dropdown", "value"))
    def update_results_graph(column):
        return results_graph(non_outlier_data, outlier_data, column)

    @app.callback(Output("window-container", "children"), Input("results-graph", "clickData"))
    def update_window_graph(click_data):
        if click_data is None:
            return []

        selected_point = click_data["points"][0]

        if selected_point["curveNumber"] == 0:
            window_data = non_outlier_data.iloc[selected_point["pointNumber"]]["Window"]
        elif selected_point["curveNumber"] == 1:
            window_data = outlier_data.iloc[selected_point["pointNumber"]]["Window"]

        return [dcc.Graph(figure=window_graph(window_data))]

    app.run_server(debug=debug, dev_tools_silence_routes_logging=True)


if __name__ == "__main__":
    signal = rhv.data.get_example_data()
    preprocessed = rhv.preprocess(signal)
    analyzed = rhv.analyze(preprocessed)
    visualize(analyzed, debug=True)
