import json

output = r'E:ObjectDetectionTensorFlow.emd'

tojson = {
    "Framework": "TensorFlow",
    "ModelConfiguration": "ObjectDetectionAPI",
    "ModelFile":".\\frozen_inference_graph.pb",
    "ModelType":"ObjectionDetection",
    "InferenceFunction":".\\CustomObjectDetector.py",
    "ImageHeight":850,
    "ImageWidth":850,
    "ExtractBands":[0],

    "Classes" : [
      {
        "Value": 0,
        "Name": "Subsurface Object Detection",
        "Color": [0, 255, 0]
      }
    ]
}

with open(output, 'w') as outfile:
	json.dump(tojson, outfile, indent=4)