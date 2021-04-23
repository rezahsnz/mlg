import sqlite3
import json
import base64

# group pred requests by model
connection = sqlite3.connect('./predict.db')
cursor = connection.cursor()  
cursor.execute(f'select id, model, image from requests where preds is null')
reqs = {}
for r in cursor.fetchall():
  model = r[1]
  d = {
    'id': r[0],
    'image': base64.b64encode(r[2]).decode('utf-8')
  }
  if model in reqs:
    reqs[model].append(d)
  else:
    reqs[model] = [d]    
connection.close()

for (model, pred_list) in reqs.items():
  with open(f'reqs/{model}.json', 'w') as f:
    json.dump({'reqs': pred_list}, f)
