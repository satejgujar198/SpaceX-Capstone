
# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Handle missing payload values
spacex_df["Payload Mass (kg)"] = pd.to_numeric(
    spacex_df["Payload Mass (kg)"], errors="coerce"
)

max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a Dash application
app = dash.Dash(__name__)

# Get unique launch sites
launch_sites = sorted(spacex_df["Launch Site"].dropna().unique())

# Create the layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "fontSize": 40
            }
        ),

        html.Br(),

        # TASK 1: Launch-site dropdown
        dcc.Dropdown(
            id="site-dropdown",
            options=[
                {"label": "All Sites", "value": "ALL"}
            ] + [
                {"label": site, "value": site}
                for site in launch_sites
            ],
            value="ALL",
            placeholder="Select a Launch Site",
            searchable=True,
            clearable=False
        ),

        html.Br(),

        # TASK 2: Successful launches pie chart
        html.Div(
            dcc.Graph(id="success-pie-chart")
        ),

        html.Br(),

        html.P("Payload range (Kg):"),

        # TASK 3: Payload range slider
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=int(max_payload),
            step=1000,
            value=[int(min_payload), int(max_payload)],
            marks={
                int(value): str(int(value))
                for value in range(0, int(max_payload) + 1, 5000)
            },
            tooltip={"placement": "bottom", "always_visible": True}
        ),

        html.Br(),

        # TASK 4: Payload vs launch success scatter chart
        html.Div(
            dcc.Graph(id="success-payload-scatter-chart")
        )
    ],
    style={"padding": "20px"}
)


# TASK 2: Update the pie chart when the launch site changes
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        filtered_df = spacex_df[
            spacex_df["class"] == 1
        ]

        fig = px.pie(
            filtered_df,
            names="Launch Site",
            title="Total Successful Launches by Launch Site"
        )
    else:
        filtered_df = spacex_df[
            spacex_df["Launch Site"] == entered_site
        ]

        success_counts = (
            filtered_df["class"]
            .value_counts()
            .reindex([1, 0], fill_value=0)
        )

        fig = px.pie(
            names=["Successful", "Failed"],
            values=[
                success_counts.loc[1],
                success_counts.loc[0]
            ],
            title=f"Launch Outcomes for {entered_site}"
        )

    return fig


# TASK 4: Update scatter chart based on site and payload range
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [
        Input("site-dropdown", "value"),
        Input("payload-slider", "value")
    ]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range

    filtered_df = spacex_df[
        spacex_df["Payload Mass (kg)"].between(low, high)
    ]

    if entered_site != "ALL":
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == entered_site
        ]

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=[
            "Launch Site",
            "Payload Mass (kg)",
            "class"
        ],
        title="Payload Mass vs Launch Outcome",
        labels={
            "class": "Landing Success (1 = Success, 0 = Failure)",
            "Payload Mass (kg)": "Payload Mass (kg)",
            "Booster Version Category": "Booster Version"
        }
    )

    fig.update_yaxes(
        tickmode="array",
        tickvals=[0, 1],
        ticktext=["Failure", "Success"]
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
