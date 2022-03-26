import dataiku
import os

def do(payload, config, plugin_config, inputs):
  data_dir=dataiku.get_custom_variables()["dip.home"]
  img_path=os.path.join(data_dir,'/local/static/images/webapps')
  img_list=os.list_dir(img_path)
  choices={}
    
  for img in img_list:
    choices[img]=img;
    
  return {"choices": choices}