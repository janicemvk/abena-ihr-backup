"""
Abena IHR - Real-Time Biomarker Integration System GUI
"""

import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import asyncio
import threading
import time
import logging
from typing import Dict, List, Any

# Import the biomarker integration system
from abena_biomarker_integration import (
    RealTimeBiomarkerIntegration,
    DeviceType,
    BiometricReading
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
biomarker_system = RealTimeBiomarkerIntegration()
simulation_thread = None
simulation_running = False
patient_data = {}
alert_history = []

# Initialize Dash app with a clean, modern theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "Abena IHR - Real-Time Biomarker Monitoring"

# Function to simulate real-time data
def simulate_biomarker_data():
    global simulation_running, patient_data, alert_history
    
    patient_id = "PATIENT_001"
    
    while simulation_running:
        # Create simulated readings
        current_time = datetime.now()
        
        # Glucose simulation with time-dependent variations
        hour_of_day = current_time.hour
        # Simulate higher glucose after meals
        meal_effect = 0
        if hour_of_day in [7, 8, 12, 13, 18, 19]:  # Meal times
            meal_effect = 40
        
        glucose_value = 120 + meal_effect + np.random.normal(0, 10)
        
        # HRV simulation with stress patterns
        # Lower HRV during work hours
        if 9 <= hour_of_day <= 17:
            hrv_value = 45 + np.random.normal(0, 8)
        else:
            hrv_value = 65 + np.random.normal(0, 10)
        
        # Cortisol with circadian rhythm
        circadian_factor = 1.0 + 0.5 * np.cos(2 * np.pi * (hour_of_day - 8) / 24)
        cortisol_value = 12.0 * circadian_factor + np.random.normal(0, 2)
        
        # Create simulated patient data
        current_status = {
            'patient_id': patient_id,
            'timestamp': current_time.isoformat(),
            'active_monitors': 3,
            'biomarkers': {
                'continuous_glucose_monitor': {
                    'value': glucose_value,
                    'unit': 'mg/dL',
                    'quality': 'good',
                    'timestamp': current_time.isoformat(),
                    'confidence': 0.9
                },
                'heart_rate_variability': {
                    'value': hrv_value,
                    'unit': 'ms',
                    'quality': 'good',
                    'timestamp': current_time.isoformat(),
                    'confidence': 0.85
                },
                'cortisol_sensor': {
                    'value': cortisol_value,
                    'unit': 'μg/dL',
                    'quality': 'good',
                    'timestamp': current_time.isoformat(),
                    'confidence': 0.8
                }
            },
            'alerts': [],
            'overall_status': 'stable'
        }
        
        # Add alerts based on values
        alerts = []
        if glucose_value < 70:
            alerts.append("HYPOGLYCEMIA_ALERT")
            current_status['overall_status'] = 'critical'
        elif glucose_value > 180:
            alerts.append("HYPERGLYCEMIA_ALERT")
            current_status['overall_status'] = 'warning'
            
        if hrv_value < 20:
            alerts.append("LOW_HRV_STRESS_INDICATOR")
            current_status['overall_status'] = 'critical'
            
        if cortisol_value > 25:
            alerts.append("HIGH_CORTISOL_STRESS")
            current_status['overall_status'] = 'warning'
        
        current_status['alerts'] = alerts
        
        # Add to alert history if there are alerts
        if alerts:
            for alert in alerts:
                alert_entry = {
                    'patient_id': patient_id,
                    'alert': alert,
                    'timestamp': current_time.isoformat(),
                    'value': glucose_value if "GLUCOSE" in alert else 
                            hrv_value if "HRV" in alert else cortisol_value,
                    'device_type': 'continuous_glucose_monitor' if "GLUCOSE" in alert else
                                'heart_rate_variability' if "HRV" in alert else 'cortisol_sensor'
                }
                alert_history.append(alert_entry)
            
        # Update patient data
        if patient_id not in patient_data:
            patient_data[patient_id] = {
                'current_status': current_status,
                'history': {
                    'timestamps': [],
                    'glucose': [],
                    'hrv': [],
                    'cortisol': []
                }
            }
        else:
            # Update current status
            patient_data[patient_id]['current_status'] = current_status
            
            # Add to history
            history = patient_data[patient_id]['history']
            history['timestamps'].append(current_time.isoformat())
            history['glucose'].append(glucose_value)
            history['hrv'].append(hrv_value)
            history['cortisol'].append(cortisol_value)
            
            # Keep only the most recent data points (6 hours worth at 5 min intervals)
            max_points = 6 * 12  # 6 hours * 12 readings per hour (5 min intervals)
            if len(history['timestamps']) > max_points:
                history['timestamps'] = history['timestamps'][-max_points:]
                history['glucose'] = history['glucose'][-max_points:]
                history['hrv'] = history['hrv'][-max_points:]
                history['cortisol'] = history['cortisol'][-max_points:]
        
        # Sleep for simulated interval (5 min compressed to 5 seconds)
        time.sleep(5)

# Function to start simulation thread
def start_simulation():
    global simulation_thread, simulation_running
    
    if simulation_thread is None or not simulation_thread.is_alive():
        simulation_running = True
        simulation_thread = threading.Thread(target=simulate_biomarker_data)
        simulation_thread.daemon = True
        simulation_thread.start()
        logger.info("Simulation started")

# Function to stop simulation
def stop_simulation():
    global simulation_running
    simulation_running = False
    logger.info("Simulation stopping")

# App layout with modern design
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Abena IHR", className="display-4"),
                html.H3("Real-Time Biomarker Integration System", className="text-muted"),
            ], className="mt-4 mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Patient Status", className="card-title"),
                    dbc.Badge("Stable", id="status-badge", color="success", className="ml-2")
                ], className="d-flex justify-content-between align-items-center"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Patient ID:"),
                            html.P(id="patient-id", className="lead")
                        ], width=4),
                        dbc.Col([
                            html.H6("Active Monitors:"),
                            html.P(id="active-monitors", className="lead")
                        ], width=4),
                        dbc.Col([
                            html.H6("Last Updated:"),
                            html.P(id="last-updated", className="lead")
                        ], width=4)
                    ]),
                    
                    html.H5("Current Alerts", className="mt-3"),
                    html.Div(id="current-alerts", className="mt-2")
                ])
            ], className="shadow mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Current Biomarker Values")),
                dbc.CardBody([
                    dbc.Row([
                        # Glucose Card
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("Glucose", className="card-title"),
                                    html.H2(id="glucose-value", className="display-4 text-primary"),
                                    html.P(id="glucose-unit", className="text-muted"),
                                    html.P(id="glucose-quality", className="small")
                                ])
                            ], className="text-center h-100")
                        ], width=4),
                        
                        # HRV Card
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("Heart Rate Variability", className="card-title"),
                                    html.H2(id="hrv-value", className="display-4 text-success"),
                                    html.P(id="hrv-unit", className="text-muted"),
                                    html.P(id="hrv-quality", className="small")
                                ])
                            ], className="text-center h-100")
                        ], width=4),
                        
                        # Cortisol Card
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("Cortisol", className="card-title"),
                                    html.H2(id="cortisol-value", className="display-4 text-warning"),
                                    html.P(id="cortisol-unit", className="text-muted"),
                                    html.P(id="cortisol-quality", className="small")
                                ])
                            ], className="text-center h-100")
                        ], width=4)
                    ])
                ])
            ], className="shadow mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Biomarker Trends")),
                dbc.CardBody([
                    dcc.Graph(id="trend-graph", config={'displayModeBar': False})
                ])
            ], className="shadow mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Alert History")),
                dbc.CardBody([
                    html.Div(id="alert-history-table")
                ])
            ], className="shadow mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Simulation Controls")),
                dbc.CardBody([
                    dbc.Button("Start Simulation", id="start-simulation", color="success", className="mr-2"),
                    dbc.Button("Stop Simulation", id="stop-simulation", color="danger", className="ml-2"),
                    html.Div(id="simulation-status", className="mt-3")
                ])
            ], className="shadow mb-4")
        ], width=12)
    ]),
    
    # Interval component for regular updates
    dcc.Interval(
        id='interval-component',
        interval=2*1000,  # Update every 2 seconds
        n_intervals=0
    ),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("© 2023 Abena IHR - Real-Time Biomarker Integration System", className="text-muted text-center")
        ])
    ])
    
], fluid=True, className="p-4")

# Callbacks

# Simulation control callbacks
@app.callback(
    Output("simulation-status", "children"),
    [Input("start-simulation", "n_clicks"),
     Input("stop-simulation", "n_clicks")],
    prevent_initial_call=True
)
def control_simulation(start_clicks, stop_clicks):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    if button_id == "start-simulation":
        start_simulation()
        return html.Div([
            html.I(className="fas fa-check-circle text-success mr-2"),
            "Simulation running - generating real-time biomarker data"
        ])
    
    elif button_id == "stop-simulation":
        stop_simulation()
        return html.Div([
            html.I(className="fas fa-stop-circle text-danger mr-2"),
            "Simulation stopped"
        ])
    
    return no_update

# Update patient status callback
@app.callback(
    [Output("patient-id", "children"),
     Output("active-monitors", "children"),
     Output("last-updated", "children"),
     Output("status-badge", "children"),
     Output("status-badge", "color"),
     Output("current-alerts", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_patient_status(n):
    if not patient_data or "PATIENT_001" not in patient_data:
        return "No data", "0", "N/A", "No data", "secondary", "No alerts"
    
    patient_id = "PATIENT_001"
    status = patient_data[patient_id]['current_status']
    
    # Format last updated time
    try:
        last_updated_time = datetime.fromisoformat(status['timestamp'])
        last_updated = last_updated_time.strftime("%Y-%m-%d %H:%M:%S")
    except:
        last_updated = "Unknown"
    
    # Set status badge
    status_text = status['overall_status'].capitalize()
    status_color = {
        "stable": "success",
        "warning": "warning",
        "critical": "danger"
    }.get(status['overall_status'], "secondary")
    
    # Format alerts
    alerts = status['alerts']
    if not alerts:
        alert_display = html.P("No active alerts", className="text-success")
    else:
        alert_items = []
        for alert in alerts:
            alert_class = "text-danger" if "CRITICAL" in alert or "HYPO" in alert else "text-warning"
            alert_items.append(
                html.Div([
                    html.I(className="fas fa-exclamation-triangle mr-2"),
                    html.Span(alert.replace("_", " "))
                ], className=f"{alert_class} mb-2")
            )
        alert_display = html.Div(alert_items)
    
    return (
        patient_id,
        str(status['active_monitors']),
        last_updated,
        status_text,
        status_color,
        alert_display
    )

# Update current biomarker values
@app.callback(
    [Output("glucose-value", "children"),
     Output("glucose-unit", "children"),
     Output("glucose-quality", "children"),
     Output("hrv-value", "children"),
     Output("hrv-unit", "children"),
     Output("hrv-quality", "children"),
     Output("cortisol-value", "children"),
     Output("cortisol-unit", "children"),
     Output("cortisol-quality", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_biomarker_values(n):
    if not patient_data or "PATIENT_001" not in patient_data:
        return "N/A", "", "", "N/A", "", "", "N/A", "", ""
    
    patient_id = "PATIENT_001"
    status = patient_data[patient_id]['current_status']
    biomarkers = status['biomarkers']
    
    # Glucose
    glucose = biomarkers.get('continuous_glucose_monitor', {})
    glucose_value = f"{glucose.get('value', 'N/A'):.1f}" if 'value' in glucose else "N/A"
    glucose_unit = glucose.get('unit', '')
    glucose_quality = f"Quality: {glucose.get('quality', 'unknown').capitalize()}"
    
    # HRV
    hrv = biomarkers.get('heart_rate_variability', {})
    hrv_value = f"{hrv.get('value', 'N/A'):.1f}" if 'value' in hrv else "N/A"
    hrv_unit = hrv.get('unit', '')
    hrv_quality = f"Quality: {hrv.get('quality', 'unknown').capitalize()}"
    
    # Cortisol
    cortisol = biomarkers.get('cortisol_sensor', {})
    cortisol_value = f"{cortisol.get('value', 'N/A'):.1f}" if 'value' in cortisol else "N/A"
    cortisol_unit = cortisol.get('unit', '')
    cortisol_quality = f"Quality: {cortisol.get('quality', 'unknown').capitalize()}"
    
    return (
        glucose_value, glucose_unit, glucose_quality,
        hrv_value, hrv_unit, hrv_quality,
        cortisol_value, cortisol_unit, cortisol_quality
    )

# Update trend graph
@app.callback(
    Output("trend-graph", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_trend_graph(n):
    if not patient_data or "PATIENT_001" not in patient_data:
        # Return empty plot
        return {
            "data": [],
            "layout": {
                "title": "No data available",
                "height": 400,
            }
        }
    
    patient_id = "PATIENT_001"
    history = patient_data[patient_id]['history']
    
    # Convert timestamps to datetime
    timestamps = [datetime.fromisoformat(ts) for ts in history['timestamps']]
    
    # Create the figure with subplots
    fig = go.Figure()
    
    # Add glucose trace
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=history['glucose'],
        name='Glucose (mg/dL)',
        mode='lines',
        line=dict(color='#007bff', width=2),
        hovertemplate='%{y:.1f} mg/dL<br>%{x}<extra>Glucose</extra>'
    ))
    
    # Add HRV trace
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=history['hrv'],
        name='HRV (ms)',
        mode='lines',
        line=dict(color='#28a745', width=2),
        hovertemplate='%{y:.1f} ms<br>%{x}<extra>HRV</extra>',
        yaxis='y2'
    ))
    
    # Add cortisol trace
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=history['cortisol'],
        name='Cortisol (μg/dL)',
        mode='lines',
        line=dict(color='#ffc107', width=2),
        hovertemplate='%{y:.1f} μg/dL<br>%{x}<extra>Cortisol</extra>',
        yaxis='y3'
    ))
    
    # Update layout with multiple y-axes
    fig.update_layout(
        title='Biomarker Trends',
        height=500,
        margin=dict(l=60, r=60, t=60, b=60),
        hovermode='closest',
        plot_bgcolor='white',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        yaxis=dict(
            title='Glucose (mg/dL)',
            titlefont=dict(color='#007bff'),
            tickfont=dict(color='#007bff'),
            gridcolor='#f0f0f0'
        ),
        yaxis2=dict(
            title='HRV (ms)',
            titlefont=dict(color='#28a745'),
            tickfont=dict(color='#28a745'),
            overlaying='y',
            side='right',
            position=0.95
        ),
        yaxis3=dict(
            title='Cortisol (μg/dL)',
            titlefont=dict(color='#ffc107'),
            tickfont=dict(color='#ffc107'),
            overlaying='y',
            side='right',
            position=1.0,
            anchor='free'
        )
    )
    
    # Add range slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeslider_thickness=0.05,
        gridcolor='#f0f0f0'
    )
    
    return fig

# Update alert history table
@app.callback(
    Output("alert-history-table", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_alert_history(n):
    if not alert_history:
        return html.P("No alerts recorded")
    
    # Sort alerts by timestamp (newest first)
    sorted_alerts = sorted(
        alert_history, 
        key=lambda x: datetime.fromisoformat(x['timestamp']), 
        reverse=True
    )
    
    # Create the alert table
    table_header = [
        html.Thead(html.Tr([
            html.Th("Time"),
            html.Th("Alert"),
            html.Th("Biomarker"),
            html.Th("Value")
        ]))
    ]
    
    rows = []
    for alert in sorted_alerts[:10]:  # Show only the 10 most recent alerts
        device_type = alert['device_type']
        alert_name = alert['alert'].replace("_", " ")
        timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%H:%M:%S")
        
        # Determine alert severity for styling
        if "HYPO" in alert['alert'] or "CRITICAL" in alert['alert']:
            row_class = "table-danger"
        elif "HIGH" in alert['alert'] or "WARNING" in alert['alert']:
            row_class = "table-warning"
        else:
            row_class = ""
        
        rows.append(html.Tr([
            html.Td(timestamp),
            html.Td(alert_name),
            html.Td(device_type.replace("_", " ").title()),
            html.Td(f"{alert['value']:.1f}")
        ], className=row_class))
    
    table_body = [html.Tbody(rows)]
    
    return dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050) 