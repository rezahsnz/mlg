import flask
import io
import json
import sqlite3
import uuid
import hashlib

app = flask.Flask(__name__)

AvailableModels = [
  'densenet121',
  'densenet169',
  'densenet201',
  'nasnet_large',
  'nasnet_mobile',
  'resnet50',
  'resnet101',
  'resnet152',
  'resnet50v2',
  'resnet101v2',
  'resnet152v2',
  'vgg16',
  'vgg19',
  'xception',
  'inception_v3',
  'inception_resnet_v2',
]

@app.route('/')
def hello():
  return '''<h1 align="center">mlg: A decentralized CNN classification service based on Golem.</h1>
            <h3>Available models</h3>
              <ul>
                <li>DenseNet121</li>
                <li>DenseNet169</li>
                <li>DenseNet201</li><br/>
                <li>ResNet50</li>
                <li>ResNet101</li>
                <li>ResNet152</li>
                <li>ResNet50V2</li>
                <li>ResNet101V2</li>
                <li>ResNet152V2</li><br/>
                <li>XCeption</li><br/>
                <li>Inception_ResNet_V2</li><br/>
                <li>Inception_V3</li>                
                <li>VGG16</li>
                <li>VGG19</li>
              </ul>
              <p>Request a prediction using cURL:  <font color="blue">curl -X POST -F image=@kitten.jpg 'http://185.221.237.140/requestPrediction/[model]'</font> 
                 and then a new request key is generated for you.
              </p>
              <p>Read the results of a previously requested input: <font color="blue">http://185.221.237.140/readPrediction/[request-id]</font>
              </p> 
         '''

@app.route('/requestPrediction/<model>', methods=['POST'])
def requestPrediction(model):
  if flask.request.method != 'POST':
    return flask.jsonify({
      'success': False,
      'reason': 'Only HTTP POST is allowed.'
    })  
  if model not in AvailableModels:
    return flask.jsonify({
      'success': False,
      'reason': f'{model} is not available, available models {AvailableModels}'
    })
  image = flask.request.files['image'].read()
  connection = sqlite3.connect('./pool/predict.db')
  cursor = connection.cursor()
  cursor.execute(
    '''create table if not exists requests(
         id text not null,
         model text not null,
         image blob not null,
         preds text)
    ''')
  req_id = hashlib.sha224(uuid.uuid4().hex.encode('utf-8')).hexdigest()
  cursor.execute(f'insert into requests(id, model, image) values(?, ?, ?)',
                 [req_id, model, image])
  connection.commit()
  connection.close()
  return flask.jsonify({
    'success': True,
    'req_id': req_id    
  })

@app.route('/readPrediction/<req_id>', methods=['POST', 'GET'])
def readPrediction(req_id):
  if flask.request.method != 'POST' and flask.request.method != 'GET':
    return flask.jsonify({
      'success': False,
      'reason': 'Only HTTP GET/POST is allowed.'
    })
  connection = sqlite3.connect('./pool/predict.db')
  cursor = connection.cursor()  
  cursor.execute(f'select preds from requests where id = "{req_id}"')
  preds = cursor.fetchone()
  connection.close()

  return flask.jsonify({
    'preds': preds[0] if preds else None  
  })

if __name__ == '__main__':
  app.run(debug=True)
  