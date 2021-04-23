import sqlite3
import json
import base64
import os
import sys

preds = {}
directory = 'out/'
for entry in os.scandir('./out'):
  if entry.path.endswith(".json") and entry.is_file():
    with open(entry.path, 'r') as f:
      preds.update(json.load(f))
if not preds:
  print('Nothing to be done.')
  sys.exit()

# group pred requests by model
connection = sqlite3.connect('./predict.db')
cursor = connection.cursor()  
for (req_id, pred) in preds.items():  
  cursor.execute('update requests set preds = ? where id = ?', (str(pred), req_id))   
connection.commit()
connection.close()
