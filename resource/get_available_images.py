import dataiku
import os

def do(payload, config, plugin_config, inputs):
  data_dir=dataiku.get_custom_variables()["dip.home"]
  img_list=os.listdir(data_dir+'/local/static/images/webapps')

  choices=[]
    
  for img in img_list:
    new_val={}
    new_val["value"]=img
    new_val["label"]=img.split('.')[0]
    choices.add(new_val)
  
  print(str(choices))
  return {"choices": choices}