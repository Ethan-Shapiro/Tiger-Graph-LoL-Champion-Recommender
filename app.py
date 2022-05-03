# %%
# !pip install pyTigerGraph
# !pip install -q jupyter-dash
# !pip install python-dotenv
# !pip install dash-cytoscape
# !pip install dash-bootstrap-components

# %%
# Imports
import json
import pandas as pd
import numpy as np
import pyTigerGraph as tg
import dash
from dash import html, dcc, dash_table, Dash
from dash.dependencies import Input, Output
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import plotly.express as px

# %%
# Connection Params
hostname = 'https://leaguerecommender.i.tgcloud.io/'
username = 'tigergraph'
password = 'tigergraph'
graphname = 'ChampionRecommendation'

# %%
conn = tg.TigerGraphConnection(
    host=hostname, username=username, password=password, graphname=graphname)
conn.apiToken = conn.getToken(conn.createSecret())

print("Connected!")

# %% [markdown]
# ### Create App

# %%
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# %% [markdown]
# ### Load champion names and lane names

# %%
# Get champion names
champion_names = ["Aatrox", "Ahri", "Akali", "Akshan", "Alistar",
                  "Amumu", "Anivia", "Annie", "Aphelios", "Ashe",
                  "AurelionSol", "Azir", "Bard", "Blitzcrank",
                  "Brand", "Braum", "Caitlyn", "Camille", "Cassiopeia",
                  "Chogath", "Corki", "Darius", "Diana", "Draven",
                  "DrMundo", "Ekko", "Elise", "Evelynn", "Ezreal",
                  "Fiddlesticks", "Fiora", "Fizz", "Galio", "Gangplank",
                  "Garen", "Gnar", "Gragas", "Graves", "Gwen", "Hecarim",
                  "Heimerdinger", "Illaoi", "Irelia", "Ivern", "Janna",
                  "Jarvaniv", "Jax", "Jayce", "Jhin", "Jinx", "Kaisa",
                  "Kalista", "Karma", "Karthus", "Kassadin", "Katarina",
                  "Kayle", "Kayn", "Kennen", "Khazix", "Kindred", "Kled",
                  "Kogmaw", "Leblanc", "Leesin", "Leona", "Lillia", "Lissandra",
                  "Lucian", "Lulu", "Lux", "Malphite", "Malzahar", "Maokai",
                  "Masteryi", "Missfortune", "MonkeyKing", "Mordekaiser",
                  "Morgana", "Nami", "Nasus", "Nautilus", "Neeko", "Nidalee",
                  "Nocturne", "Nunu", "Olaf", "Orianna", "Ornn", "Pantheon",
                  "Poppy", "Pyke", "Qiyana", "Quinn", "Rakan", "Rammus", "Reksai",
                  "Rell", "Renekton", "Rengar", "Riven", "Rumble", "Ryze",
                  "Samira", "Sejuani", "Senna", "Seraphine", "Sett", "Shaco",
                  "Shen", "Shyvana", "Singed", "Sion", "Sivir", "Skarner",
                  "Sona", "Soraka", "Swain", "Sylas", "Syndra", "Tahmkench",
                  "Taliyah", "Talon", "Taric", "Teemo", "Thresh", "Tristana",
                  "Trundle", "Tryndamere", "Twistedfate", "Twitch", "Udyr",
                  "Urgot", "Varus", "Vayne", "Veigar", "Velkoz", "Vex", "Vi",
                  "Viego", "Viktor", "Vladimir", "Volibear", "Warwick",
                  "Xayah", "Xerath", "Xinzhao", "Yasuo", "Yone", "Yorick",
                  "Yuumi", "Zac", "Zed", "Zeri", "Ziggs", "Zilean", "Zoe", "Zyra"]

# %%
# Set different lanes
lanes = ['Top', 'Jg', 'Mid', 'Bot', 'Sup']
# %%


def champion_select_dropdown():
    return dcc.Dropdown(id='dropdown-update-champion',
                        value='Aatrox',
                        options=champion_names,
                        clearable=False,
                        searchable=True,
                        style={
                            "width": "98%",
                            "marginLeft": "1rem",
                            "marginTop": "1rem",
                        }
                        )


def getNetwork(main_champion):

    def top_func(x):
        return [(0, -85), (0, -170), (0, -250)][x]

    def jg_func(x):
        return [(60, -60), (130, -130), (200, -200)][x]

    def mid_func(x):
        return [(80, 0), (160, 0), (250, 0)][x]

    def bot_func(x):
        return [(60, 60), (130, 130), (200, 200)][x]

    def sup_func(x):
        return [(0, 85), (0, 170), (0, 250)][x]

    # Run query
    comms = conn.runInstalledQuery(
        "GetAllRecs", params={"mainChampion": main_champion})[0]['@@edgeList']

    color_map = {'top_rec': 'yellow', 'jg_rec': 'green',
                 'mid_rec': 'blue', 'bot_rec': 'red', 'sup_rec': 'purple'}
    positions = {'top_rec': 0, 'jg_rec': 0,
                 'mid_rec': 0, 'bot_rec': 0, 'sup_rec': 0}
    positions_funcs = {'top_rec': top_func, 'jg_rec': jg_func,
                       'mid_rec': mid_func, 'bot_rec': bot_func, 'sup_rec': sup_func}
    vertices = {}
    els = []

    # Table args
    lanes = []
    distances = []
    champion_name = []

    for entry in comms:
        if 'reverse' in entry['e_type']:
            continue

        # Get to and from nodes
        source = entry['from_id']
        target = entry['to_id']
        edge_type = entry['e_type']
        random_num = str(np.random.randint(0, 100))

        # Add initial mainChampion
        if source not in vertices:
            if source == main_champion:
                # els.append({'data': {'id': source, 'label': source}, 'classes': 'orange'})
                els.append({'data': {'id': source, 'label': source}, 'position': {
                           'x': 0, 'y': 0}, 'locked': True, 'classes': 'orange'})

        # Add our target if not already present
        if target not in vertices:
            # els.append({'data': {'id': target+random_num, 'label': target}, 'classes': color_map[edge_type]})

            # Custom layout
            x, y = positions_funcs[edge_type](positions[edge_type])
            positions[edge_type] += 1
            els.append({'data': {'id': target+random_num, 'label': target}, 'position': {
                       'x': x, 'y': y}, 'locked': True, 'classes': color_map[edge_type]})

        # Add from and to
        els.append({'data': {'source': source, 'target': target+random_num}})

        # TABLE VALUES
        # Extract lane
        lane = entry['e_type'].split('_')[0].capitalize()

        # Add values to table args
        lanes.append(lane)
        dist = 1-entry['attributes']['dist']
        distances.append("{:0.4%}".format(dist))
        champion_name.append(target)

    # Add legend nodes
    els.append({
        'data': {'id': 'top_color_legend', 'label': 'Top'},
        'position': {'x': -100, 'y': -250},
        'classes': 'yellow',
        'locked': True
    })

    els.append({
        'data': {'id': 'jg_color_legend', 'label': 'Jg'},
        'position': {'x': -100, 'y': -125},
        'classes': 'green',
        'locked': True
    })

    els.append({
        'data': {'id': 'mid_color_legend', 'label': 'Mid'},
        'position': {'x': -100, 'y': 0},
        'classes': 'blue',
        'locked': True
    })

    els.append({
        'data': {'id': 'bot_color_legend', 'label': 'Bot'},
        'position': {'x': -100, 'y': 125},
        'classes': 'red',
        'locked': True
    })

    els.append({
        'data': {'id': 'sup_color_legend', 'label': 'Sup'},
        'position': {'x': -100, 'y': 250},
        'classes': 'purple',
        'locked': True
    })

    # Create cytoscape network
    stylesheet = [{'selector': 'node',
                   'style': {
                       'content': 'data(label)'
                   }
                   }]

    for color in color_map.values():
        stylesheet.append({
                          'selector': f'.{color}',
                          'style': {
                              'background-color': color,
                          }
                          }
                          )
    stylesheet.append({
        'selector': '.orange',
        'style': {
            'background-color': 'orange'
        }
    })

    network = cyto.Cytoscape(
        id='cytoscape',
        elements=els,
        layout={'name': 'circle'},
        stylesheet=stylesheet,
        style={'width': '100%', 'height': '571px', 'marginRight': '100px'},
        userPanningEnabled=False,
        userZoomingEnabled=False
    )

    # Create Table
    table_df = pd.DataFrame(data=(zip(champion_name, lanes, distances)), columns=[
                            'Champion', 'Lane', 'Similarity'])
    table_df = table_df.sort_values(['Lane', 'Similarity'], ascending=False)
    # Sort by list
    sorter = ['Top', 'Jg', 'Mid', 'Bot', 'Sup']
    table_df = table_df.set_index('Lane')
    table_df = table_df.loc[sorter, :].reset_index()

    table = html.Div(
        dash_table.DataTable(table_df.to_dict('records'), columns=[{"name": i, "id": i} for i in table_df.columns], id='champion-table',
                             cell_selectable=False,
                             style_header={'backgroundColor': 'lightgrey',
                                           'fontWeight': 'bold',
                                           },
                             ),
        style={'overflowY': 'scroll',
               'height': 500}
    )

    return network, table


def get_new_elements(main_champion: str):

    def top_func(x):
        return [(0, -85), (0, -170), (0, -250)][x]

    def jg_func(x):
        return [(60, -60), (130, -130), (200, -200)][x]

    def mid_func(x):
        return [(80, 0), (160, 0), (250, 0)][x]

    def bot_func(x):
        return [(60, 60), (130, 130), (200, 200)][x]

    def sup_func(x):
        return [(0, 85), (0, 170), (0, 250)][x]

    # Run query
    comms = conn.runInstalledQuery(
        "GetAllRecs", params={"mainChampion": main_champion})[0]['@@edgeList']

    color_map = {'top_rec': 'yellow', 'jg_rec': 'green',
                 'mid_rec': 'blue', 'bot_rec': 'red', 'sup_rec': 'purple'}
    positions = {'top_rec': 0, 'jg_rec': 0,
                 'mid_rec': 0, 'bot_rec': 0, 'sup_rec': 0}
    positions_funcs = {'top_rec': top_func, 'jg_rec': jg_func,
                       'mid_rec': mid_func, 'bot_rec': bot_func, 'sup_rec': sup_func}
    vertices = {}
    els = []

    # Table args
    lanes = []
    distances = []
    champion_name = []

    for entry in comms:
        if 'reverse' in entry['e_type']:
            continue

        # Get to and from nodes
        source = entry['from_id']
        target = entry['to_id']
        edge_type = entry['e_type']
        random_num = str(np.random.randint(0, 1000))

        # Add initial mainChampion
        if source not in vertices:
            if source == main_champion:
                # els.append({'data': {'id': source, 'label': source}, 'classes': 'orange'})

                # Custom layout
                els.append({'data': {'id': source, 'label': source}, 'position': {
                           'x': 0, 'y': 0}, 'locked': True, 'classes': 'orange'})

        # Add our target if not already present
        if target not in vertices:
            # els.append({'data': {'id': target+random_num, 'label': target}, 'classes': color_map[edge_type]})

            # Custom layout
            x, y = positions_funcs[edge_type](positions[edge_type])
            positions[edge_type] += 1
            els.append({'data': {'id': target+random_num, 'label': target}, 'position': {
                       'x': x, 'y': y}, 'locked': True, 'classes': color_map[edge_type]})

        # Add from and to
        els.append({'data': {'source': source, 'target': target+random_num}})

        # TABLE VALUES
        # Extract lane
        lane = entry['e_type'].split('_')[0].capitalize()

        # Add values to table args
        lanes.append(lane)
        dist = 1-entry['attributes']['dist']
        distances.append("{:0.2%}".format(dist))
        champion_name.append(target)

    els.append({
        'data': {'id': 'top_color_legend', 'label': 'Top'},
        'position': {'x': -100, 'y': -250},
        'classes': 'yellow',
        'locked': True
    })

    els.append({
        'data': {'id': 'jg_color_legend', 'label': 'Jg'},
        'position': {'x': -100, 'y': -125},
        'classes': 'green',
        'locked': True
    })

    els.append({
        'data': {'id': 'mid_color_legend', 'label': 'Mid'},
        'position': {'x': -100, 'y': 0},
        'classes': 'blue',
        'locked': True
    })

    els.append({
        'data': {'id': 'bot_color_legend', 'label': 'Bot'},
        'position': {'x': -100, 'y': 125},
        'classes': 'red',
        'locked': True
    })

    els.append({
        'data': {'id': 'sup_color_legend', 'label': 'Sup'},
        'position': {'x': -100, 'y': 250},
        'classes': 'purple',
        'locked': True
    })

    table_df = pd.DataFrame(data=(zip(champion_name, lanes, distances)), columns=[
                            'Champion', 'Lane', 'Similarity'])
    table_df = table_df.sort_values(['Lane', 'Similarity'], ascending=False)
    # Sort by list
    sorter = ['Top', 'Jg', 'Mid', 'Bot', 'Sup']
    table_df = table_df.set_index('Lane')

    return els, table_df.loc[sorter, :].reset_index()


@app.callback(Output('cytoscape', 'elements'),
              Output('champion-table', 'data'),
              Input('dropdown-update-champion', 'value'))
def update_champion_graph(value):
    (els, table_df) = get_new_elements(value)
    return els, table_df.to_dict('records')


@app.callback(
    Output('champion-table', 'style_data_conditional'),
    Input('cytoscape', 'selectedNodeData'))
def highlightSelectedNodeInTable(data):
    if not data:
        return dash.no_update

    champ = [nodeData['label'] for nodeData in data][-1]
    return [{'if': {'filter_query': '{Champion} =' + champ},
            'backgroundColor': 'yellow'}]


def champion_recommendations_card():
    (network, table) = getNetwork('Aatrox')

    graph_layout_dropdown = dcc.Dropdown(id='dropdown-update-layout',
                                         value='circle',
                                         clearable=False,
                                         options=[
                                             {'label': name.capitalize(),
                                              'value': name}
                                             for name in ['grid', 'random', 'circle', 'cose', 'concentric']
                                         ])

    network_card = dbc.Card([
        dbc.CardBody([
            html.H1("If you play Aatrox, try:",
                    id='main-graph-title', className='card-title'),
            # graph_layout_dropdown,
            network,
        ])
    ],
        outline=True,
        color='info',
        style={
            "width": "100%",
            "marginRight": "1rem",
            "marginTop": "1rem",
            "marginBottom": "1rem"
    }
    )

    table_card = dbc.Card([
        dbc.CardBody([
            html.H1('Top 3 Champions per Lane', className='card-title'),
            html.P("Recommendations for other champions to play in every lane.",
                   className='card-body'),
            table
        ])
    ],
        outline=True,
        color='info',
        style={
        "marginTop": "1rem",
        "marginBottom": "1rem",
        "marginLeft": "1rem",
        'maxwidth': '692px'
    }
    )

    return network_card, table_card


def champsWhoRecStats(main_champion: str):
    lane_counts = conn.runInstalledQuery(
        "GetWhoRec", params={"mainChampion": main_champion})[0]['LaneCount']

    if len(lane_counts) == 0:
        return {'None': 1}, 0, 'None'

    sorted_lane_counts = sorted(
        lane_counts.items(), key=lambda lane: lane[1], reverse=True)
    highest_lane = sorted_lane_counts[0][0]
    count = sorted_lane_counts[0][1]

    return lane_counts, count, highest_lane.capitalize()


def who_rec_pie_chart(lane_counts):
    lanes = [x.capitalize() for x in list(lane_counts.keys())]
    counts = list(lane_counts.values())

    pie = px.pie(values=counts,
                 names=lanes,
                 hole=0.2,
                 width=800,
                 height=500)

    pie.update_layout(width=800, title_x=0.5, showlegend=False,
                      margin=dict(l=10, r=10, t=10, b=10))
    pie.update_traces(textposition='inside',
                      textinfo='label+percent',
                      )

    return pie


def champions_who_rec_card():
    (lane_counts, count, lane) = champsWhoRecStats('Aatrox')

    pie = who_rec_pie_chart(lane_counts)

    return dbc.Card([
        dbc.CardBody([
            html.H1("Lane distribution that recommends: Aatrox",
                    id='who-recommends-title', className='card-title'),
            dbc.Row([
                dbc.Col([dcc.Graph(id='piechart', figure=pie)], width=8),
                dbc.Col([html.P(f'Recommended the most by: {lane}', id='most-recommended-by'), html.P(
                    f'Number who recommend me: {count}', id='num-who-recommend')], width=4)
            ])
        ])
    ],
        outline=True,
        color='info',
        style={
        "width": "50%",
        "marginLeft": "1rem",
        "marginTop": "1rem",
        "marginBottom": "1rem"
    }
    )


@app.callback(Output('num-who-recommend', 'children'),
              Output('most-recommended-by', 'children'),
              Output('who-recommends-title', 'children'),
              Output('main-graph-title', 'children'),
              Output('piechart', 'figure'),
              Input('dropdown-update-champion', 'value'))
def updateChampionsWhoRec(main_champion: str):
    (lane_counts, count, lane) = champsWhoRecStats(main_champion)
    num_who_rec = f'Number who recommend me: {count}'
    rec_by_most = f'Recommended the most by: {lane}'
    who_rec_title = f"Lane distribution that recommends: {main_champion}"
    main_graph_title = f'If you play {main_champion}, try:'
    return num_who_rec, rec_by_most, who_rec_title, main_graph_title, who_rec_pie_chart(lane_counts)


def title_card():
    return dbc.Card([
        dbc.CardBody([
                    html.Center(
                        html.H1("League of Legends Champion Recommender", className='card-title')),
                    ])
    ],
        color='light',  # Options include: primary, secondary, info, success, warning, danger, light, dark
        style={
        "width": "98rem",
        "marginLeft": "1rem",
        "marginTop": "1rem",
        "marginBottom": "1rem"
    }
    )


network_card, table_card = champion_recommendations_card()


app.layout = html.Div(
    children=[
        html.Div([], className='col-2'),
        dbc.Row([title_card(),
                 champion_select_dropdown()],
                justify='center'),
        dbc.Row([
            html.Div([table_card], className='col-6'),
            html.Div([network_card], className='col-6')
        ]),
        dbc.Row([champions_who_rec_card()], justify='center'),
        html.Div([], className='col-2')
    ],
    className="row")

if __name__ == '__main__':
    app.run_server(debug=False, port=8051)

# %%
