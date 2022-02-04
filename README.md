
<h1 align="center">CNN predict services on top of Golem</h1>

## Theme
The basic idea is to distribute popular CNNs pre-trained with ImageNet datasets across Golem provider nodes. Once we have enough images(CNNs) on the board, then we setup an HTTP REST API server that collects predict requests. At regular times, say every 10 minutes, a script is invoked to batch requests and have them sent to the nodes for prediction. Once the requests are fulfilled, the results are recorded on the db and ready to be queried.  

## Available models
The following models are available to be used:  
- DenseNet121
- DenseNet169
- DenseNet201  
- ResNet50
- ResNet101
- ResNet152  
- ResNet50V2
- ResNet101V2
- ResNet152V2  
- VGG16
- VGG19 
- NASNet_large
- NASNet_mobile
- XCeption  
- Inception_V3  
- Inception_ResNet_V2  

## Batching
The batching script is invoked at regular times to look for any pending requests. The pending requests are then grouped by their models and divided into chunks of 16 to make sure that the payload(task data) a provider receives is capped at 64mb(with max 2mb per request data for HTTP POST). Grouping followed by request chunks introduces a hierarchy of task paralellization that improves the scalablility of the server while making sure that each node receives enough payload to be worth the time it spends loading the large images. At times of low demand, however, the nodes might not receive enough requests. 


## Invocation
To ask for a predicttion on some image file, one can make a simple cURL call:  
`curl -X POST -F image=@kitten.jpg 'BASEURL/requestPrediction/[model]'`  
This schedules the request for prediction and a request_id is generated. The Caller can then query for the results using a call like this:  
`curl -X POST 'BASEURL/readPrediction/[request-id]'`  
A typical result for a previsouly requested prediction is either `null`(as being not picked up yet) or an array of predicted classes.  


## Caveat
Please note that as we are in the beta phase and running the testnet nodes so you might experience difficulties.

# setup
The provided scripts are for reference only.

## Refrences
- [Golem](https://golem.network)  
- [Keras applications](https://github.com/keras-team/keras-applications)  
