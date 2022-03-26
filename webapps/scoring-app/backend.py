from dataiku.customwebapp import *

# Access the parameters that end-users filled in using webapp config
# For example, for a parameter called "input_dataset"
# input_dataset = get_webapp_config()["input_dataset"]

import dash
import dash_table
import dash_bootstrap_components as dbc

from dash import dcc
from dash import html

from dataiku.customrecipe import *

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import dataikuapi
import dataiku

import time
import numpy as np

import os


#-------------------------------------------------------------------------------------
#sample_data="customer_data_clean_copy"

# keep_fields=['customer_id','ip','ip_geopoint']

header_img="https://www.dataiku.com/wp-content/uploads/2021/02/Dataiku-new-logo-teal.svg"
right_img="/local/static/images/webapps/How-to-make-Customer-value-proposition.jpeg"

#client = dataikuapi.APINodeClient("http://localhost:20300", "CLV_Project")
#model_endpoint="High_Revenue_Customers"

text_on_button="Predict!"
pred_false_pic='/local/static/images/webapps/Rejected-Stamp-PNG-Clipart.png'
pred_true_pic='/local/static/images/webapps/approved-icon.png'

#--------------------------------------------------------------------------------------

max_categories=150
max_slider=100

#--------------------------------------------------------------------------------------

# import plugin config

# import variables
# var_list=dataiku.get_custom_variables()
keep_fields=get_plugin_config()['included_columns']

#header_img=get_plugin_config()['header_img']
#right_img=get_plugin_config()['right_image']
#pred_true_pic=get_plugin_config()['true_image']
#pred_false_pic=get_plugin_config()['false_image']

#max_categories=get_plugin_config()['max_categories']
#max_slider=get_plugin_config()['max_slider']

# api_node=var_list["api_node_address"]
# api_project=var_list["api_project"]
# model_endpoint=var_list["api_model_endpoint"]

#api_node=get_plugin_config()['api_address']
#api_project=get_plugin_config()['api_service']
#model_endpoint=get_plugin_config()['api_endpoint']

client = dataikuapi.APINodeClient("http://localhost:20300", "CLV_Project")

#client=dataikuapi.APINodeClient(api_address,api_service)

# path=str(dataiku.get_custom_variables()["dip.home"])+"/local/static/images/webapps"
# test=os.listdir(path) # returns list
# print(test)

# import dataset
dataset=dataiku.Dataset(get_plugin_config['input_dataset'])
df=dataset.get_dataframe()

df=df.keep(columns=keep_fields)

fields=dict(df.dtypes)
print(str(fields))

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
    'textAlign':'centre'
}

pic_style={
    "margin":"20px",
    'padding': 10,
    "verticalAlign":'middle',
    'horizontalAlign':'middle'
}

def generate_input(key):
    type=fields[key]

    my_div=[html.P('{}:'.format(key.title().replace('_',' ')), style=text_style)]
    try:
        if type=="number":
            my_min=df[key].min()
            my_max=df[key].max()

            if my_max-my_min <=max_slider:
                my_div=my_div+[html.Div(dcc.Slider(id=key, min=my_min, max=my_max, step=1, value=my_min, marks=None, tooltip={"placement": "bottom", "always_visible": True}), style=tool_style)]
            else:
                my_div=my_div+[dbc.Input(id=key, type=type, debounce=True, placeholder=key.title().replace('_',' '), style=tool_style)]


        elif type=="text":
            my_list=sorted(list(df[key].unique()))

            if len(my_list) <=max_categories:
                my_div=my_div+[html.Div(dcc.Dropdown(id=key, options=my_list, value=my_list[0], placeholder=key.title().replace('_',' ')), style=tool_style)]
            else:
                my_div=my_div+[dbc.Input(id=key, type=type, debounce=True, placeholder=key.title().replace('_',' '), style=tool_style)]
                
        elif type=="bool":
            my_div=my_div+[html.Div(dcc.RadioItems(id=key, options=[{'label':'True ','value':True }, {'label':'False ','value':False}], value='False', inline=True, labelStyle={
                    'display': 'inline-block',
                    'margin-right': '10px'}), style=tool_style)]
            
        else:
            my_div=my_div+[dbc.Input(id=key, type=type, debounce=True, placeholder=key.title().replace('_',' '), style=tool_style)]

    except:
        my_div=my_div+[dbc.Input(id=key, type=type, debounce=True, placeholder=key.title().replace('_',' '), style=tool_style)]

    return dbc.Row(my_div)



app.layout = html.Div([
        dbc.Row(html.Img(style={'height':'100px'}, src=header_img)),
        html.Br(),
    
        dbc.Row([
            dbc.Col([
#                 dcc.Checklist(
#                     id="campaign_old",
#                     options=[
#                        {'label': 'Campaign', 'value': 'True'}
#                     ]
#                 ),

                html.Div([
                 generate_input(key) for key in fields
                ])
            ]),
            dbc.Col([
                html.Div(html.Img(src=right_img, style={'height':'250px'}), style=pic_style),
                html.Br(),
                html.Div(html.Button(text_on_button, id='btn-nclicks-1', n_clicks=0), style={'horizonalAlign':'middle','verticalAlign': 'middle', 'display': 'inline'}),
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
        my_image=pred_false_pic
    else:    
        my_image=pred_true_pic
    return my_image
    

# @app.callback(
#     Output("pred-pic","src"),
#     Input('btn-nclicks-1', 'n_clicks'), prevent_initial_call=True
# )
# def trigger_loading('clicks'):
#     print(str(vals))
#     my_image="test"
#     return my_image




