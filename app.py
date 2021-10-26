import json

from flask import Flask, render_template, request, jsonify
from gevent.pywsgi import WSGIServer
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)

print('Model loaded. Check http://127.0.0.1:5000/')

MODEL_PATH = 'models/ecg_model.h5'

# Load your own trained model
model = load_model(MODEL_PATH)
model._make_predict_function()  # Necessary,多线程并发前预先编译
print('Model loaded. Start serving...')

classes = np.array(['N', 'A', 'V', 'L', 'R'])


@app.route('/', methods=['GET'])
def hello_world():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        if request.json == "":
            return jsonify(result='null', probability=0)
        dic = json.loads(request.json)
        leads = dic['leads']
        size = dic['size']
        data = dic['data']
        # print("leads : {0}, size : {1}".format(leads, size))
        # print(data)
        preds = model_predict(data, model)
        # print("preds : {0}".format(preds))
        pred_proba = np.amax(preds, axis=1)
        pred_index = np.argmax(preds, axis=1)
        pred_class = classes[pred_index]
        return jsonify(result=pred_class.tolist(), probability=pred_proba.tolist())
    return None


def model_predict(data, model):
    x = np.array(data)
    x = np.expand_dims(x, axis=2)
    preds = model.predict(x)
    return preds


if __name__ == '__main__':
    # app.run(port=5002, threaded=False)

    # Serve the app with gevent
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
