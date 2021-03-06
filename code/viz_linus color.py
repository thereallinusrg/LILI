##############################
#
# Choose Inno Nr Here:
inno_choose = 'inno_31'
single_color = True
#
#
##############################

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import configparser as configparser

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

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

    df= df.set_index(['date', 'twitter_id']) 

    df = df[['lat', 'lng', 'created_at']].copy()

    # Filling nan values with 0
    df = df.dropna()

    # Compute bubble sizes
    df['size'] = 3 #df[inno_choose]

    # Compute bubble color
    if single_color == True:
        df['color'] = 'fuchsia'
    else:
        df["created_at_int"] = pd.to_datetime(df['created_at'])
        df["time_int"] = df["created_at_int"].apply(lambda x:x.toordinal())

        norm = matplotlib.colors.Normalize(vmin= df["time_int"].min(),vmax= df["time_int"].max(), clip=True)
        mapper = plt.cm.ScalarMappable(norm=norm, cmap=plt.cm.viridis) #viridis can be changed for other color palette
        df['color']  = df["time_int"].apply(lambda x: mcolors.to_hex(mapper.to_rgba(x)))

  
    
    return df

def DayExpander(df):
    df_perm = pd.DataFrame()
    idprev = 0

    for idx, data in df.groupby(level=0):
        new = df.loc[idx]
        if idprev != 0:
            old = df_perm.loc[idprev] 
            join = pd.concat([old, new])
        else:
            join = new
        
        join['date'] = idx
        join.set_index('date', append=True, inplace=True)
        join = join.reorder_levels(['date', 'twitter_id'])

        df_perm = pd.concat([df_perm, join])
        
    
        idprev = idx
        
    return(df_perm)

df = process_geocodedtwitter_data(df)
df = DayExpander(df) #This is an iterative process, it takes a while

days = df.index.levels[0].tolist()

frames = [{   
    'name':'frame_{}'.format(day),
    'data':[{
        'type':'scattermapbox',
        'lat':df.xs(day)['lat'],
        'lon':df.xs(day)['lng'],
        'marker':go.scattermapbox.Marker(
            size=df.xs(day)['size']*3,
            color= df.xs(day)['color'],
            showscale=False,
            #colorbar={'title':'Innovations', 'titleside':'top', 'thickness':4, 'tickprefix':' Inno Nr.: '},
        )#,
        #'customdata':np.stack((df.xs(day)['confirmed_display'], df.xs(day)['recovered_display'],  df.xs(day)['deaths_display'], pd.Series(df.xs(day).index)), axis=-1),
        #'hovertemplate': "<extra></extra><em>%{customdata[3]}  </em><br>????  %{customdata[0]}<br>????  %{customdata[1]}<br>??????  %{customdata[2]}",
    }],           
} for day in days] 

sliders = [{
    'transition':{'duration': 0},
    'x':0.08, 
    'len':0.88,
    'currentvalue':{'font':{'size':15}, 'prefix':'???? ', 'visible':True, 'xanchor':'center'},  
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
        'label':'????', # Play
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
        'zoom':2.5,
        'style':"carto-darkmatter",
        
    }
)

# Creating the figure
fig = go.Figure(data=data, layout=layout, frames=frames)
fig.update_layout(title_text=f'Linuguistic Diffusion of {inno_choose}')

# Displaying the figure
fig.show()