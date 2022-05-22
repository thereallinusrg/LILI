##############################
#
# Choose Inno Nr Here:
inno_choose = 'inno_01'
#
#
##############################

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import configparser as configparser

config = configparser.ConfigParser()
config.read('/home/linusrg/Code/LILI/config.ini')
mapbox_token = config['mapbox']['secret_token']

df = pd.read_csv('/home/linusrg/Code/LILI/code/inno_geocoded.csv')
df = df.dropna(subset=['lng', 'lat'])

df['innoint'] = df.inno_nr.str.strip('inno_').astype('int')
df['date'] = pd.to_datetime(df['created_at']).dt.date

zone = 'country_y'
def process_geocodedtwitter_data(df, zone = 'country_y', inno_choose=inno_choose):

    # Choose Innovation
    df = df[df.inno_nr == inno_choose]
    df = df.reset_index()

    # Saving countries positions (latitude and longitude per subzones)
    country_position = df[[f'{zone}', 'lat', 'lng']].drop_duplicates([f'{zone}']).set_index([f'{zone}'])

    # Pivoting per category
    cats = list(df.inno_nr.unique())
    cats.sort()
    
    df = pd.pivot_table(df, values='innoint', index=['date', f'{zone}'], columns=['inno_nr'])
    df.columns = cats

    # Merging locations after pivoting
    df = df.join(country_position)

    # Filling nan values with 0
    df = df.fillna(0)

    # Compute bubble sizes
    df['size'] = df[inno_choose]

    # Compute bubble color
    df['color'] = 'fuchsia' #df[cats].sum(axis=1)
    
    return df

df = process_geocodedtwitter_data(df)

days = df.index.levels[0].tolist()

frames = [{   
    'name':'frame_{}'.format(day),
    'data':[{
        'type':'scattermapbox',
        'lat':df.xs(day)['lat'],
        'lon':df.xs(day)['lng'],
        'marker':go.scattermapbox.Marker(
            size=df.xs(day)['size']*20,
            color=df.xs(day)['color'],
            showscale=False,
            colorbar={'title':'Innovations', 'titleside':'top', 'thickness':4, 'tickprefix':' Inno Nr.: '},
        )#,
        #'customdata':np.stack((df.xs(day)['confirmed_display'], df.xs(day)['recovered_display'],  df.xs(day)['deaths_display'], pd.Series(df.xs(day).index)), axis=-1),
        #'hovertemplate': "<extra></extra><em>%{customdata[3]}  </em><br>🚨  %{customdata[0]}<br>🏡  %{customdata[1]}<br>⚰️  %{customdata[2]}",
    }],           
} for day in days] 

sliders = [{
    'transition':{'duration': 0},
    'x':0.08, 
    'len':0.88,
    'currentvalue':{'font':{'size':15}, 'prefix':'📅 ', 'visible':True, 'xanchor':'center'},  
    'steps':[{'label':str(day),
            'method':'animate',
            'args':[
                ['frame_{}'.format(day)],
                {'mode':'immediate', 'frame':{'duration':100, 'redraw': True}, 'transition':{'duration':50}}
              ],
        } for day in days]
}]

play_button = [{
    'type':'buttons',
    'showactive':True,
    'x':0.045, 'y':-0.08,
    'buttons':[{ 
        'label':'🎬', # Play
        'method':'animate',
        'args':[
            None,
            {
                'frame':{'duration':100, 'redraw':True},
                'transition':{'duration':50},
                'fromcurrent':True,
                'mode':'immediate',
            }
        ]
    }]
}]

# Defining the initial state
data = frames[0]['data']

# Adding all sliders and play button to the layout
layout = go.Layout(
    sliders=sliders,
    updatemenus=play_button,
    mapbox={
        'accesstoken':mapbox_token,
        'center':{'lat':7, 'lon':-33},
        'zoom':1.7,
        'style':"open-street-map",
        
    }
)

# Creating the figure
fig = go.Figure(data=data, layout=layout, frames=frames)
fig.update_layout(title_text=f'Linuguistic Diffusion of {inno_choose}')

# Displaying the figure
fig.show()