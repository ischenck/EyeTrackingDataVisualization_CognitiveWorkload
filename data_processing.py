import numpy as np
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import math

def load_file(path, names):
    if not path.is_file():
        raise FileNotFoundError(str(path))
        
    data = pd.read_csv(path, sep="\t", names=names, header=None)
    return data

def load_datasets():
    EVD_cols = ["time", "event", "event_key", "data_1", "data_2", "description"]
    FXD_cols = ["fix_number", "timestamp", "duration", "gazepoint_x", "gazepoint_y"]
    GZD_cols = ["gazepoint_X_L" ,"gazepoint_Y_L", "cam_X_L", "cam_Y_L",
                "distance_L", "pupil_L", "validity_L", "gazepoint_X_R",
                "gazepoint_Y_R", "cam_X_R", "cam_Y_R", "distance_R", "pupil_R", 
                 "validity_R"]
    path = Path.cwd() / "p4"
    graphEVD = load_file(path / "p4.graphEVD.txt", EVD_cols)
    graphFXD = load_file(path / "p4.graphFXD.txt", FXD_cols)
    graphGZD = load_file(path / "p4.graphGZD.txt", GZD_cols)
    treeEVD = load_file(path / "p4.treeEVD.txt", EVD_cols)
    treeFXD = load_file(path / "p4.treeFXD.txt", FXD_cols)
    treeGZD = load_file(path / "p4.treeGZD.txt", GZD_cols)
    GZD = load_file(path /"p4GZD.txt", GZD_cols)
    return graphEVD, graphFXD, graphGZD, treeEVD, treeFXD, treeGZD, GZD

def remove_invalid_data(GZD):
    indexNames = GZD[(GZD['validity_L'] > 0) | (GZD['validity_R'] > 0)].index
    GZD.drop(indexNames, inplace=True)
    return GZD

def calculate_saccade_length(FXD):
    x = np.square(FXD[['gazepoint_x', 'gazepoint_y']].diff())
    x = np.sqrt(x['gazepoint_x'] + x['gazepoint_y'])
    x = x.fillna(0.)
    return x

graphEVD, graphFXD, graphGZD, treeEVD, treeFXD, treeGZD, GZD = load_datasets()

graphGZD = remove_invalid_data(graphGZD)
treeGZD = remove_invalid_data(treeGZD)
GZD = remove_invalid_data(GZD)

graphFXD['saccade_length'] = calculate_saccade_length(graphFXD)

treeFXD['saccade_length'] = calculate_saccade_length(treeFXD)

#randomized event and dilation for now
event_names = ['LMouseButton', 'Keyboard', 'RMouseButton']
graphFXD['event'] = np.random.choice(event_names, size=len(graphFXD))
graphFXD['dilation'] = np.random.choice(10000, size=len(graphFXD))

hover_text = []
bubble_size = []

for index, row in graphFXD.iterrows():
    hover_text.append(('Fixation Duration: {duration}<br>'+
                        'Saccade Length: {saccade_length}<br>')
                        .format(duration=row['duration'], 
                        saccade_length=row['saccade_length']))
    bubble_size.append(math.sqrt(row['dilation']))

graphFXD['text'] = hover_text
graphFXD['size'] = bubble_size
sizeref = 2.*max(graphFXD['size'])/(100**2)

event_data = {event:graphFXD.query("event == '%s'" %event) for event in event_names}

fig = go.Figure() 

for event_name, event in event_data.items():
    fig.add_trace(go.Scatter(
        x=event['duration'], y=event['saccade_length'],
        name=event_name, text = event['text'],
        marker_size=event['size']
    ))

fig.update_traces(mode='markers', marker=dict(sizemode='area', sizeref=sizeref, line_width=2))

fig.update_layout(
    title='Fixation Duration v. Saccade Length',
    xaxis=dict(title='Fixation Duration', gridcolor='white', gridwidth=2,),
    yaxis=dict(title='Saccade Length', gridcolor='white', gridwidth=2,),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
)

fig.show()