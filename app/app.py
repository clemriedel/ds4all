# Import modules
import os
import pandas as pd
import flask.views
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from werkzeug import secure_filename
from flask_weasyprint import HTML, render_pdf
from nlq import clem_lda

# Initialize the Flask application
app = Flask(__name__, static_url_path = "", static_folder='static')
app.secret_key = "bacon"

# Set the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Set extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'csv'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nlq')
def nlq():
    return render_template('index.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/clem')
def clem():
    return render_template('clem.html')

@app.route('/dspipeline_code')
def dspipeline_code():
    return render_template('dspipeline_code.html')

@app.route('/clem_pipeline')
def clem_pipeline():
    return render_template('clem_pipeline.html')



@app.route('/predict', methods=['POST'])
def predcit():
    file_name = request.form['file_name']
    files = os.listdir('uploads')
    if file_name not in files:
        return 'File does not exist. Did you upload your file? Did you type in the extension .csv before submitting?'

    a = ('uploads/{}'.format(file_name))
    input_file = pd.read_csv(a)
    if len(input_file) > 3100:
        return render_template('index.html')
    else:
        z,text_name,f_name = clem_lda(a)
        return render_template('prediction.html', topics = z, title = text_name, f_name = f_name) 






# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        #return 1
        #redirect(url_for('uploaded_file', filename=filename))
        return redirect("/")


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/return_clean_data/')
def return_clean_data():
    return send_file('data/clean_data_nlq.py', as_attachment = True, 
                    attachment_filename = 'clean_data_nlq')




#########
projects_names = ['NSF_chem_2013', 'NSF_bio_2015', 'NSF_cosmology',
                'NSF_etno', 'NSF_history', 'NSF_politics', 'NSF_plasma', 'NSF_phy_2013']

@app.route('/return/<name>/')
def return_name(name):
    if name in projects_names:
        return send_file('./data/{}.csv'.format(name), as_attachment = True, 
                        attachment_filename = name)


# @app.route('/predict/<name>', methods=['POST'])
# def predict_name(name):
#     if name in projects_names:
#         fixed_file_name = '{}.csv'.format(name)
#         files = os.listdir('data')
#         a = ('data/{}'.format(fixed_file_name))
#         z,text_name,f_name = clem_lda(a)
#         return render_template('prediction.html', topics = z, title = text_name, f_name = f_name)


@app.route('/predict/<name>', methods=['POST'])
def predict_name(name):
    if name in projects_names:
        return render_template('prediction_{}.html'.format(name))

@app.route('/stat_pdf/<name>')
def stat_pdf(name):
    return render_template('prediction_{}.html'.format(name))


@app.route('/print_pdf/<name>/')
def print_pdf(name):
    if name in projects_names:
        print name
        return render_pdf('/stat_pdf/{}'.format(name))




@app.route('/dspipeline')
def dspeipeline():
    return render_template('dspipeline_home.html')

class View(flask.views.MethodView):
    def get(self):
        return flask.render_template('index.html')

    def post(self):
        result = eval(flask.request.form['expression'])
        flask.flash(result)
        return self.get()
    
app.add_url_rule('/', view_func=View.as_view('main'), methods=['GET', 'POST'])

app.debug = True
app.threaded = True
app.run()


