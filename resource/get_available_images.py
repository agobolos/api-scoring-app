import dataiku
import os

def do(payload, config, plugin_config, inputs):
  data_dir=dataiku.get_custom_variables()["dip.home"]
  #img_path=os.path.join(data_dir,'/local/static/images/webapps')
  img_list=os.listdir(data_dir+'/local/static/images/webapps')
  print(str(img_list))
  choices={}
    
  for img in img_list:
    choices[img]=img
  
  print(str(choices))
  return {"choices": choices}