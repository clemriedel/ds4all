#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import flask
from flask import Flask, render_template, request, jsonify
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import pymongo
import predict
import json
import time
from datetime import datetime
import socket
import requests
import bokeh
import hashlib
import pandas as pd
import numpy as np

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
PORT = 5353
REGISTER_URL = "http://10.3.32.217:5000/register"
DATA = []
TIMESTAMP = []

client = pymongo.MongoClient()
db = client['fraud-streaming']
col = db['test_data']

model = predict.get_model()
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8


colors = {
    'Black': '#000000',
    'Red':   '#FF0000',
    'Green': '#00FF00',
    'Blue':  '#0000FF',
}

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

@app.route('/score', methods=['POST'])
def score():
    jsons = json.dumps(request.json, sort_keys=True, indent=4, separators=(',', ':'))
    m = hashlib.sha224(jsons).hexdigest()
    if col.find_one({'_id': m}) is None:
       print "New Point"
       timepoint = time.time()

       datapoint_dict = json.loads(jsons)
       df = pd.DataFrame.from_dict(datapoint_dict, orient='index').T
       df = predict.clean_json(df)
       predictions = predict.get_predictions(df, model)
       datapoint_dict['predicts'] = tuple(predictions[0])
       datapoint_dict['time'] = timepoint

       datapoint_json = json.dumps(datapoint_dict)

       col.insert_one({'_id': m, 'data': datapoint_json})
    else:
        print "Seen this point"
    return ""


@app.route('/barchart')
def barchart():
    return render_template('pages/placeholder.barchart.html')

@app.route('/check')
def check():
    line1 = "Number of data points: {0}".format(len(DATA))
    if DATA and TIMESTAMP:
        dt = datetime.fromtimestamp(TIMESTAMP[-1])
        data_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        line2 = "Latest datapoint received at: {0}".format(data_time)
        line3 = DATA[-1]
        output = "{0}\n\n{1}\n\n{2}".format(line1, line2, line3)
    else:
        output = line1
    return output, 200, {'Content-Type': 'text/css; charset=utf-8'}


def register_for_ping(ip, port):
    registration_data = {'ip': ip, 'port': port}
    requests.post(REGISTER_URL, data=registration_data)


########################
# Joe Warren's Work

def colorbar(flag, percent):
    """Summary: Return a colorbar for the id, given its percent and a flag of fraud/not fraud etc.
    """
    html_output = """
        <div class="progress">
          <div class="progress-bar progress-bar-{}" role="progressbar" aria-valuenow="{}" aria-valuemin="0" aria-valuemax="100" style="width: {}%">
            <span class="sr-only">{}%</span>
          </div>
        </div>
    """.format(flag, percent, percent, percent)
    return html_output

@app.route('/_get_detail', methods = ['GET'])
def get_detail():
    """Summary: Get the detail of a given event.
    """
    detail_id = request.args.get('id')
    print detail_id

    result = col.find_one({'_id':detail_id})
    print result.keys()
    
    this_id = result['_id']
    this_data = result['data']
    
    detail = this_data
    #this_data = json.loads(this_data)
    
    #detail = this_data['description']
    
    print "Detail Called"
    html_output = """
                    <div class="">
                    <p>{}</p>
                    </div>
                  """.format(detail)

    return jsonify(result=html_output)


@app.route('/_get_queue')
def get_queue():
    """Summary: Construct html for Queue of items streaming into /scoure route.
    """
    html_output = '<div class="list-group">'

    results = col.find({})


    result_list = []
    index_list = []
    for result in results:

        #result = col.find({'_id': detail_id})
        this_id = result['_id']
        this_data = result['data']
        this_data = json.loads(this_data)

        detail = this_data['description']
        result_list.append([this_id, this_data ])
        index_list.append(this_data['predicts'][1])
    result_list = np.array(result_list)
    index_list = np.array(index_list)
    index_list = np.argsort(index_list)
    result_list = result_list[index_list[::-1]]
    
    for result in result_list:
        html_output += '<button type="button" class="list-group-item test_record" data-id="{}">'.format(result[0]) 
        # Replace with actual fields
        html_output += 'Name: ' + result[1]['name'] + '<br />'
        html_output += 'Rating: ' + str(result[1]['predicts'][1]) 
        html_output += '</button>' 
    
    html_output += '</div>'

    return jsonify(result=html_output)

@app.route('/eventlist')
def eventlist():
    return render_template('pages/placeholder.eventlist.html')

########################
# Prebuilt - Ignore

@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    ip_address = socket.gethostbyname(socket.gethostname())
    print "attempting to register %s:%d" % (ip_address, PORT)
    register_for_ping(ip_address, str(PORT))
    app.run(host= ip_address, port=PORT, debug=True)
