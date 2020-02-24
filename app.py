import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import dash_bio as dashbio
import pandas as pd

import json

# protein data
# shamelessly borrowed from https://github.com/plotly/dash-bio-docs-files/tree/master/mol3d
with open("data/model_data.js", "r") as f:
    model_data = json.load(f)

with open("data/styles_data.js", "r") as f:
    styles_data = json.load(f)


color_palette = ["rgb(128, 0, 96)", "rgb(230, 115, 0)", "rgb(255, 191, 0)"]

# microarray data

# data example from https://data.mendeley.com/datasets/ynp2tst2hh/4
df = pd.read_excel("data/Gordon-2002_LungCancer.xlsx", index_col=0, skiprows=[1])
df = df.iloc[:100, :7] # slicing dataframe for simpler heatmap

data = df.values

# dashboard layout
app = dash.Dash("Example", external_stylesheets=[dbc.themes.DARKLY])
app.title = "Example"
app.layout = dbc.Tabs(
    [
        dbc.Tab(
            html.Div(
                [
                    dashbio.Molecule3dViewer(
                        id="my-dashbio-molecule3d",
                        styles=styles_data,
                        modelData=model_data,
                    ),
                    "Selection data",
                    html.Hr(),
                    html.Div(id="molecule3d-output"),
                ]
            ),
            label="3D protein",
        ),
        dbc.Tab(
            dcc.Graph(
                figure=dashbio.Clustergram(
                    data=data,
                    hidden_labels=["row"],
                    height=900,
                    width=1400,
                    column_labels=list(df.columns.values),
                    row_labels=list(df.index),
                    color_threshold={"row": 150, "col": 700},
                    color_map=[
                        [0.0, color_palette[0]],
                        [0.5, color_palette[1]],
                        [1.0, color_palette[2]],
                    ],
                    color_list={
                        "row": [color_palette[0], color_palette[1], color_palette[2]],
                        "col": [color_palette[1], color_palette[2], color_palette[0]],
                        "bg": "rgb(255,255,255)",
                    },
                    annotation_font=dict(color="white", size=10),
                    tick_font=dict(size=15, color="rgb(200,200,200)"),
                )
            ),
            label="Microarray Heatmap",
        ),
    ]
)

# Plotly dash callbacks
@app.callback(
    dash.dependencies.Output("molecule3d-output", "children"),
    [dash.dependencies.Input("my-dashbio-molecule3d", "selectedAtomIds")],
)
def show_selected_atoms(atom_ids):
    if atom_ids is None or len(atom_ids) == 0:
        return "No atom has been selected. Click somewhere on the molecular \
        structure to select an atom."
    return [
        html.Div(
            [
                html.Div("Element: {}".format(model_data["atoms"][atm]["element"])),
                html.Div("Chain: {}".format(model_data["atoms"][atm]["chain"])),
                html.Div(
                    "Residue name: {}".format(model_data["atoms"][atm]["residue_name"])
                ),
                html.Br(),
            ]
        )
        for atm in atom_ids
    ]


if __name__ == "__main__":
    app.run_server(debug=True)
