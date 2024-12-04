import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
        
import warnings
warnings.filterwarnings('ignore')

import plotly.io as pio
pio.renderers.default='notebook'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime


appearances = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\appearances.csv")
club_games = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\club_games.csv")
clubs = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\clubs.csv")
competitions = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\competitions.csv")
game_events = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\game_events.csv")
game_lineups = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\game_lineups.csv")
games = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\games.csv")
player_valuations = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\player_valuations.csv")
players = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\players.csv")

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
        
import warnings
warnings.filterwarnings('ignore')

import plotly.io as pio
pio.renderers.default='notebook'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime


appearances = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\appearances.csv")
club_games = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\club_games.csv")
clubs = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\clubs.csv")
competitions = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\competitions.csv")
game_events = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\game_events.csv")
game_lineups = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\game_lineups.csv")
games = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\games.csv")
player_valuations = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\player_valuations.csv")
players = pd.read_csv("C:\\Users\\anhuy\\Desktop\\ĐỒ ÁN PYTHON\\DATA\\players.csv")



team = 'Manchester United'
season = 2023
team_id = players[(players['current_club_name'].str.contains(team,case=False)) & 
                  (players['last_season'] == season)]['current_club_id'].iat[0]

def filter_by_season(dataset,season):
    
    # Filter for year 2023 and months from August to December
    year1 = (dataset['date'].dt.year == season) & (dataset['date'].dt.month >= 8)
    
    # Filter for year 2024 and months from January to June
    year2 = (dataset['date'].dt.year == (season + 1)) & (dataset['date'].dt.month <=6)
    
    filtered_data = dataset[year1 | year2]
    
    return filtered_data
players['date_of_birth'] = pd.to_datetime(players['date_of_birth'])

players['age'] = datetime.now().year - players['date_of_birth'].dt.year

appearances['date'] = pd.to_datetime(appearances['date'])

appearances23_24 = filter_by_season(appearances,season)

appearances23 = appearances23_24[(appearances23_24['player_current_club_id']) == team_id]

game_list = appearances23['game_id'].to_list()

club_games23 = club_games[(club_games['game_id'].isin(game_list)) & (club_games['club_id'] == team_id)]

club = clubs[clubs['club_id'] == team_id]

game_events['date'] = pd.to_datetime(game_events['date'])

game_events23 = filter_by_season(game_events, season)

game_events23 = game_events23[game_events23['club_id'] == team_id]

games23 = games[(games['game_id'].isin(game_list)) & ((games['home_club_id']==team_id) | (games['away_club_id']==team_id))]

players23 = players[((players['last_season'] == season) & (players['current_club_id'] == team_id))]

player_list= players23['player_id'].to_list()

player_valuations['date'] = pd.to_datetime(player_valuations['date'])

player_valuations23 = player_valuations[(player_valuations['player_id'].isin(player_list)) & (player_valuations['current_club_id'] == team_id)]

player_valuations23 = filter_by_season(player_valuations23,season)

game_lineups23 = game_lineups[(game_lineups['game_id'].isin(game_list)) & (game_lineups['player_id'].isin(player_list))]

club

premierleague_teams = ['Tottenham Hotspur Football Club', 'Association Football Club Bournemouth',
                          'Liverpool Football Club', 'Brighton and Hove Albion Football Club',
                          'Nottingham Forest Football Club', 'Luton Town Football Club',
                       'Newcastle United Football Club','Brentford Football Club',
                       'Crystal Palace Football Club', 'West Ham United Football Club',
                          'Fulham Football Club', 'Burnley Football Club', 'Arsenal Football Club',
                      'Manchester City Football Club', 'Aston Villa Football Club',
                       'Wolverhampton Wanderers Football Club','Sheffield United Football Club', 
                       'Everton Football Club','Chelsea Football Club', 'Manchester United Football Club']

premier_clubs = clubs[(clubs['domestic_competition_id'] == 'GB1') & 
                      (clubs['name'].isin(premierleague_teams))]

premier_teams_id = premier_clubs['club_id'].to_list()

player_valuations_pl = filter_by_season(player_valuations,season)

player_valuations_pl = player_valuations_pl[player_valuations_pl['current_club_id'].isin(premier_teams_id)].groupby('current_club_id')['market_value_in_eur'].sum().reset_index()

premier_clubs = pd.merge(premier_clubs, player_valuations_pl, how='left', left_on='club_id', 
                         right_on='current_club_id')

premier_clubs['total_market_value'] = premier_clubs['market_value_in_eur']

premier_clubs.drop(['current_club_id', 'market_value_in_eur'], axis=1, inplace=True)

import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Đảm bảo premier_clubs có cột 'average_age' và 'name'
sort_by_age = premier_clubs.sort_values('average_age', ascending=False)

# Sử dụng Plotly để vẽ biểu đồ
fig = go.Figure(go.Bar(
    x=sort_by_age['average_age'],
    y=sort_by_age['name'],
    orientation='h',  # Chỉ ra rằng các cột sẽ nằm ngang
    marker=dict(color=sort_by_age['average_age'], colorscale="Teal"),
))

# Cập nhật giao diện của biểu đồ
fig.update_layout(
    height=700,
    title='Average Squad Age in Every Premier League Team',
    plot_bgcolor='rgb(56,0,60)',
)

fig.update_yaxes(title_text='Team', showgrid=False)
fig.update_xaxes(title_text='Average Age (in Squad)', showgrid=False)

# Hiển thị biểu đồ
fig.show()
