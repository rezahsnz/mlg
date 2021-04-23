import tensorflow as tf
from tensorflow.keras.applications import imagenet_utils
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
import numpy as np
import json
from PIL import Image
import base64
import io

Models = {
  'densenet121': { 
    'class': tf.keras.applications.DenseNet121,
    'preprocess': tf.keras.applications.densenet.preprocess_input,
    'weights': './weights/densenet121_weights_tf_dim_ordering_tf_kernels.h5'
  },
  'densenet169': { 
    'class': tf.keras.applications.DenseNet169,
    'preprocess': tf.keras.applications.densenet.preprocess_input,
    'weights': './weights/densenet169_weights_tf_dim_ordering_tf_kernels.h5'
  },
  'densenet201': { 
    'class': tf.keras.applications.DenseNet201,
    'preprocess': tf.keras.applications.densenet.preprocess_input,
    'weights': './weights/densenet201_weights_tf_dim_ordering_tf_kernels.h5'
  },
}

params = {}
with open('/golem/work/params.json') as f:
  params = json.load(f)
M = Models[params['model']]
images = []
for req in params['reqs']:
  b = base64.b64decode(req['image'].encode('ascii'))
  image = Image.open(io.BytesIO(b)).resize((224, 224))
  if image.mode != "RGB":
    image = image.convert("RGB")
  image = img_to_array(image)
  images.append(image)
images = M['preprocess'](np.array(images))
model = M['class'](weights=M['weights'])
raw_preds = imagenet_utils.decode_predictions(model.predict(images))
preds = [[(p[0], p[1], p[2].astype(float)) for p in pred] for pred in raw_preds]
d = {}
i = 0
for p in preds:
  req = params['reqs'][i]
  d[req['id']] = p
  i = i + 1
with open(f'/golem/output/preds.json', 'w') as f:
  json.dump(d, f)
