from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
import json
import os
import plotly

app = Flask(__name__)

# Read the data file
data_file_path = os.path.join(os.path.dirname(__file__), 'synthetic_data.csv')
synthetic_data = pd.read_csv(data_file_path)

# Ensure that the timestamp column is formatted as a datetime
synthetic_data['timestamp'] = pd.to_datetime(synthetic_data['timestamp'], errors='coerce')

# Summarise emissions by month and calculate cumulative emissions
synthetic_data['month'] = synthetic_data['timestamp'].dt.to_period('M')
monthly_emissions = synthetic_data.groupby('month')['emissions'].sum().reset_index()
monthly_emissions['month'] = monthly_emissions['month'].dt.to_timestamp()
monthly_emissions.columns = ['date', 'monthly_emissions']

# Calculate cumulative emissions
monthly_emissions['cumulative_emissions'] = monthly_emissions['monthly_emissions'].cumsum()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot')
def plot():
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=monthly_emissions['date'], 
            y=monthly_emissions['cumulative_emissions'],
            mode='lines+markers',
            hovertemplate="Date=%{x}<br>Cumulative emissions=%{y}<extra></extra>"
        )
    )

    frames = [
        go.Frame(
            name=f"frame{k}",
            data=[
                go.Scatter(
                    x=monthly_emissions['date'][:k+1],
                    y=monthly_emissions['cumulative_emissions'][:k+1],
                    mode='lines+markers'
                )
            ],
            layout=go.Layout(
                xaxis=dict(
                    title='Date(Month-Year or Month-Day, depending on display)', 
                    range=[monthly_emissions['date'].min(), monthly_emissions['date'][:k+1].max()]
                ),
                yaxis=dict(
                    title='Cumulative emissions (kg CO₂-eq)',
                    range=[0, monthly_emissions['cumulative_emissions'][:k+1].max() * 1.1]
                )
            )
        )
        for k in range(len(monthly_emissions))
    ]

    fig.update_layout(
        
        xaxis=dict(title='Date(Month-Year or Month-Day, depending on display)'),
        yaxis=dict(title='Cumulative emissions (kg CO₂-eq)'),
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=12),
            itemclick="toggleothers"
        ),
        margin=dict(t=50, b=50),
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 1000, "redraw": True}, "fromcurrent": True, "transition": {"duration": 500}}]},
                {"label": "Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]},
                {"label": "Restart", "method": "animate", "args": [["frame0"], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}]},
                {"label": "End", "method": "animate", "args": [["frame" + str(len(monthly_emissions) - 1)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]}
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": True,
            "x": 0.5,
            "xanchor": "center",
            "y": -0.5,
            "yanchor": "bottom"
        }]
    )

    fig.frames = frames

    data_json = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    layout_json = json.dumps(fig.layout, cls=plotly.utils.PlotlyJSONEncoder)
    frames_json = json.dumps(fig.frames, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('plot.html', data=data_json, layout=layout_json, frames=frames_json)

@app.route('/plot2')
def plot2():
    data = synthetic_data.copy()

    # Summary of emissions by month and region and calculation of cumulative emissions
    data['month'] = data['timestamp'].dt.to_period('M')
    data_grouped = data.groupby(['region', 'month'])['emissions'].sum().reset_index()
    data_grouped['month'] = data_grouped['month'].dt.to_timestamp()
    data_grouped['cumulative_emissions'] = data_grouped.groupby('region')['emissions'].cumsum()

    # Initialise graphics
    fig = go.Figure()

    # Get all the unique areas
    regions = data_grouped['region'].unique()

    # Prepare frames
    frames = []
    max_y = 0  # Track the largest emissions to adjust the y-axis appropriately
    all_dates = sorted(data_grouped['month'].unique())
    for k, date in enumerate(all_dates):
        frame_data = []
        frame_max_y = 0  # Maximum value of the current frame
        for region in regions:
            region_data = data_grouped[(data_grouped['region'] == region) & (data_grouped['month'] <= date)]
            current_max_y = region_data['cumulative_emissions'].max()
            frame_max_y = max(frame_max_y, current_max_y)
            frame_data.append(go.Scatter(
                x=region_data['month'],
                y=region_data['cumulative_emissions'],
                mode='lines+markers',
                name=region
            ))
        max_y = max(max_y, frame_max_y)
        frames.append(go.Frame(data=frame_data, name=f"frame{k}",
                               layout=go.Layout(yaxis=dict(range=[0, frame_max_y * 1.1]))))

    # Add initial data for all regions
    for region in regions:
        region_data = data_grouped[data_grouped['region'] == region]
        fig.add_trace(
            go.Scatter(
                x=region_data['month'],
                y=region_data['cumulative_emissions'],
                mode='lines+markers',
                name=region
            )
        )

    fig.update_layout(
        xaxis=dict(title='Date(Year-Month)', tickformat='%Y-%m'),
        yaxis=dict(title='Cumulative Emissions (kg CO₂-eq)', range=[0, max_y * 1.1]),
        template="plotly_white",
        legend_title="Region",
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.3,
            font=dict(size=12),
            itemclick="toggleothers"
        ),
        margin=dict(t=50, b=50, l=0, r=200),
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 1000, "redraw": True}, "fromcurrent": True, "transition": {"duration": 500}}]},
                {"label": "Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]},
                {"label": "Restart", "method": "animate", "args": [["frame0"], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}]},
                {"label": "End", "method": "animate", "args": [["frame" + str(len(frames) - 1)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]}
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": True,
            "x": 0.5,
            "xanchor": "center",
            "y": -0.5,
            "yanchor": "bottom"
        }]
    )

    fig.frames = frames

    data_json = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    layout_json = json.dumps(fig.layout, cls=plotly.utils.PlotlyJSONEncoder)
    frames_json = json.dumps(fig.frames, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('plot2.html', data=data_json, layout=layout_json, frames=frames_json)

@app.route('/plot3')
def plot3():
    data = synthetic_data.copy()

    # Ensure that the timestamp column is formatted as a datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')

    # Summarise emissions by month and project name and calculate cumulative emissions
    data_grouped = data.groupby(['project_name', 'month'])['emissions'].sum().reset_index()
    data_grouped['month'] = data_grouped['month'].dt.to_timestamp()
    data_grouped['cumulative_emissions'] = data_grouped.groupby('project_name')['emissions'].cumsum()

    # Initialise graphics
    fig = go.Figure()

    # Get all unique project names
    projects = data_grouped['project_name'].unique()

    # Prepare frames
    frames = []
    max_y = 0  # Track the largest emissions to adjust the y-axis appropriately
    all_dates = sorted(data_grouped['month'].unique())
    for k, date in enumerate(all_dates):
        frame_data = []
        frame_max_y = 0  # Maximum value of the current frame
        for project in projects:
            project_data = data_grouped[(data_grouped['project_name'] == project) & (data_grouped['month'] <= date)]
            current_max_y = project_data['cumulative_emissions'].max()
            frame_max_y = max(frame_max_y, current_max_y)
            frame_data.append(go.Scatter(
                x=project_data['month'],
                y=project_data['cumulative_emissions'],
                mode='lines+markers',
                name=project
            ))
        max_y = max(max_y, frame_max_y)
        frames.append(go.Frame(data=frame_data, name=f"frame{k}",
                               layout=go.Layout(yaxis=dict(range=[0, frame_max_y * 1.1]))))

    # Add initial data for all items
    for project in projects:
        project_data = data_grouped[data_grouped['project_name'] == project]
        fig.add_trace(
            go.Scatter(
                x=project_data['month'],
                y=project_data['cumulative_emissions'],
                mode='lines+markers',
                name=project
            )
        )

    fig.update_layout(
        xaxis=dict(title='Date(Year-Month)', tickformat='%Y-%m'),
        yaxis=dict(title='Cumulative emissions (kg CO₂-eq)', range=[0, max_y * 1.1]),
        template="plotly_white",
        legend_title="Project Name",
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.3,
            font=dict(size=12),
            itemclick="toggleothers"
        ),
        margin=dict(t=50, b=50, l=50, r=250),
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 1000, "redraw": True}, "fromcurrent": True, "transition": {"duration": 500}}]},
                {"label": "Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]},
                {"label": "Restart", "method": "animate", "args": [["frame0"], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}]},
                {"label": "End", "method": "animate", "args": [["frame" + str(len(frames) - 1)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]}
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": True,
            "x": 0.5,
            "xanchor": "center",
            "y": -0.5,
            "yanchor": "bottom"
        }]
    )

    fig.frames = frames

    data_json = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    layout_json = json.dumps(fig.layout, cls=plotly.utils.PlotlyJSONEncoder)
    frames_json = json.dumps(fig.frames, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('plot3.html', data=data_json, layout=layout_json, frames=frames_json)

@app.route('/plot4')
def plot4():
    data = synthetic_data.copy()

    # Summarise emissions by month and whether in the cloud and calculate cumulative emissions
    data_grouped = data.groupby(['on_cloud', 'month'])['emissions'].sum().reset_index()
    data_grouped['month'] = data_grouped['month'].dt.to_timestamp()
    data_grouped['cumulative_emissions'] = data_grouped.groupby('on_cloud')['emissions'].cumsum()

    # Convert on_cloud columns to more descriptive labels
    data_grouped['on_cloud'] = data_grouped['on_cloud'].map({'Y': 'On Cloud', 'N': 'Local'})

    # Initialise graphics
    fig = go.Figure()

    # Get all unique categories for data being on the cloud or locally
    cloud_status = data_grouped['on_cloud'].unique()

    # Prepare frames
    frames = []
    max_y = 0  # Track the largest emissions to adjust the y-axis appropriately
    all_dates = sorted(data_grouped['month'].unique())
    for k, date in enumerate(all_dates):
        frame_data = []
        frame_max_y = 0  # Maximum value of the current frame
        for status in cloud_status:
            status_data = data_grouped[(data_grouped['on_cloud'] == status) & (data_grouped['month'] <= date)]
            current_max_y = status_data['cumulative_emissions'].max()
            frame_max_y = max(frame_max_y, current_max_y)
            frame_data.append(go.Scatter(
                x=status_data['month'],
                y=status_data['cumulative_emissions'],
                mode='lines+markers',
                name=status
            ))
        max_y = max(max_y, frame_max_y)
        frames.append(go.Frame(data=frame_data, name=f"frame{k}",
                               layout=go.Layout(yaxis=dict(range=[0, frame_max_y * 1.1]))))

    # Add initial data for all items
    for status in cloud_status:
        status_data = data_grouped[data_grouped['on_cloud'] == status]
        fig.add_trace(
            go.Scatter(
                x=status_data['month'],
                y=status_data['cumulative_emissions'],
                mode='lines+markers',
                name=status
            )
        )

    fig.update_layout(
        xaxis=dict(title='Date(Year-Month)', tickformat='%Y-%m'),
        yaxis=dict(title='Cumulative emissions (kg CO₂-eq)', range=[0, max_y * 1.1]),
        template="plotly_white",
        legend_title="Cloud Status",
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.3,
            font=dict(size=12),
            itemclick="toggleothers"
        ),
        margin=dict(t=50, b=50, l=50, r=250),
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 1000, "redraw": True}, "fromcurrent": True, "transition": {"duration": 500}}]},
                {"label": "Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]},
                {"label": "Restart", "method": "animate", "args": [["frame0"], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}]},
                {"label": "End", "method": "animate", "args": [["frame" + str(len(frames) - 1)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]}
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": True,
            "x": 0.5,
            "xanchor": "center",
            "y": -0.5,
            "yanchor": "bottom"
        }]
    )

    fig.frames = frames

    data_json = json.dumps(fig.data, cls=plotly.utils.PlotlyJSONEncoder)
    layout_json = json.dumps(fig.layout, cls=plotly.utils.PlotlyJSONEncoder)
    frames_json = json.dumps(fig.frames, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('plot4.html', data=data_json, layout=layout_json, frames=frames_json)



if __name__ == '__main__':
    app.run(debug=True, port=8080)
