import sqlite3
import json
from json import JSONDecodeError
import base64
import os
import sys

preds = {}
for entry in os.scandir('./requestor/out'):
  if entry.path.endswith(".json") and entry.is_file():
    with open(entry.path, 'r') as f:
      try:
        preds.update(json.load(f))
      except JSONDecodeError:
        pass
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
