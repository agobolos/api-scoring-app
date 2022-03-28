
# Access the parameters that end-users filled in using webapp config
# For example, for a parameter called "input_dataset"
# input_dataset = get_webapp_config()["input_dataset"]

import dash
import dash_bootstrap_components as dbc

from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from dataiku.customwebapp import *
import dataikuapi
import dataiku

import time
import numpy as np

#--------------------------------------------------------------------------------------

# import configuration
webapp_config=get_webapp_config()
webapp_config.update({ k:v.strip() for k, v in webapp_config.items() if isinstance(v, str)})
print("Found configuration: " + str(webapp_config))

# Import pictures and prepend location
for image in ['header','right','true','false']:
    locals()[image+'_img']='/local/static/images/webapps/'+webapp_config[str(image)+'_image']

max_categories=webapp_config['max_categories']
max_slider=webapp_config['max_slider']
text_on_button="Predict!"

# Configure API connection
model_endpoint=webapp_config['api_endpoint']
client=dataikuapi.APINodeClient(webapp_config['api_address'],webapp_config['api_service'])

# import dataset
dataset=dataiku.Dataset(webapp_config['input_dataset'])
df=dataset.get_dataframe()

df=df.drop(columns=filter(None,webapp_config['excluded_columns']))

fields=dict(df.dtypes)

for key in fields.keys():
    if fields[key]==bool:
        fields[key]=='bool'
    elif fields[key]==np.int64 or fields[key]==np.float64:
        fields[key]='number'
#     elif fields[key]==object:
    else:
        fields[key]='text'    
        
print(str(fields))

app.config.external_stylesheets = [dbc.themes.BOOTSTRAP]

tool_style= {
    'width':'40%',
    'padding':5, 
    "margin":"5px",
    "verticalAlign":'top'
}

text_style= {
    'width':'40%',
    'margin':'5px',
    'verticalAlign':'middle',
    'textAlign':'right'
}

pic_style={
    "margin":"20px",
    'padding': 10,
    "verticalAlign":'middle',
    'horizontalAlign':'middle',
    'textAlign': 'center'
}

def generate_input(key):
    type=fields[key]
    
    df_temp=df[key].dropna().unique()

    my_div=[html.P('{}:'.format(key.title().replace('_',' ')), style=text_style)]
    try:
        if type=="number":
            my_min=df_temp.min()
            my_max=df[key].max()

            if my_max-my_min <=max_slider:
                my_div=my_div+[html.Div(dcc.Slider(id=key, min=my_min, max=my_max, step=1, value=my_min, marks=None, tooltip={"placement": "bottom", "always_visible": True}), style=tool_style)]
            else:
                my_div=my_div+[dbc.Input(id=key, type=type, debounce=True, placeholder=key.title().replace('_',' '), style=tool_style)]


        elif type=="text":
            my_list=sorted(df_temp)
            print(key + " has variables: " + str(my_list))

            if len(my_list) <= max_categories:
                my_div=my_div+[html.Div(dcc.Dropdown(id=key, options=my_list, value=my_list[0], placeholder=key.title().replace('_',' ')), style=tool_style)]
            else:
                my_div=my_div+[dbc.Input(id=key, type=type, debounce=True, placeholder=key.title().replace('_',' '), style=tool_style)]
                
        elif type=="bool":
            my_div=my_div+[html.Div(dcc.RadioItems(id=key, options=[{'label':'True ','value':True }, {'label':'False ','value':False}], value='False', inline=True, labelStyle={
                    'display': 'inline-block',
                    'margin-right': '10px'}), style=tool_style)]
            
        else:
            my_div=my_div+[dbc.Input(id=key, type=type, debounce=True, placeholder=key.title().replace('_',' '), style=tool_style)]

    except Exception as e:
        print(key + " " + str(e))
        my_div=my_div+[dbc.Input(id=key, type=type, debounce=True, placeholder=key.title().replace('_',' '), style=tool_style)]

    return dbc.Row(my_div)



app.layout = html.Div([
        dbc.Row(html.Div(html.Img(style={'height':'100px'}, src=header_img), style={'textAlign': 'center'})),
        html.Br(),
    
        dbc.Row([
            dbc.Col([
                html.Div([
                    # Create the input style
                    generate_input(key) for key in fields
                ])
            ], width=6),
            dbc.Col([
                html.Div(html.Img(src=right_img, style={'height':'250px'}), style=pic_style),
                html.Br(),
                html.Div(html.Button(text_on_button, id='btn-nclicks-1', n_clicks=0), style={'textAlign':'center','verticalAlign': 'center','horizontalAlign':'center'}),
                html.Br(),
                html.Div(id="prediction"),
                html.Div(dcc.Loading(id="loading-img", children=[html.Img(id='pred-pic', style={'height':'100px'})], type='circle'), style=pic_style)
                ]
            )
    ])        
])

@app.callback(
    Output("pred-pic","src"),
    Input('btn-nclicks-1', 'n_clicks'),
    [State(my_id, "value") for my_id in fields],
    prevent_initial_call=True
)
def cb_render(btn1,*vals):
    print("my args " + str(vals))
    record_to_predict={}
    my_list=fields.keys()
    
    for (i,value) in enumerate(vals):
        if value:
            record_to_predict[list(fields)[i]]=value
        

    #print(str(record_to_predict))
    prediction = client.predict_record(model_endpoint, record_to_predict)
    #print(prediction["result"])

    time.sleep(1)
    if prediction["result"]["prediction"].lower()=="false":
        my_image=false_img
    else:    
        my_image=true_img
    return my_image
    

# @app.callback(
#     Output("pred-pic","src"),
#     Input('btn-nclicks-1', 'n_clicks'), prevent_initial_call=True
# )
# def trigger_loading('clicks'):
#     print(str(vals))
#     my_image="test"
#     return my_image




