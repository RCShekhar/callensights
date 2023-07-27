import os
import io
import boto3 as aws
from flask_app import app
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'm4a'])

# Function to check if the file is allowed or not
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home page route
@app.route('/', methods=['GET'])
def home_page():
    return jsonify("Welcom to Callensights!!")

# Upload audio file api end point
@app.route('/file-upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part

    if 'file' not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        print('No file uploaded')
        return resp
    
    # checking if the file is uploaded or not
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        print('No file selected for uploading')
        return resp
    
    # validating if the the provided is a valid audio file or not
    if file and allowed_file(file.filename):

        # if alloed audio file then load the file into GCS
        try:
            s3 = aws.client('s3')
            print(f'Bucket selected {app.config["AUDIO_BUCKET"]}')           

            response = s3.upload_fileobj(file, app.config['AUDIO_BUCKET'], file.filename)
            response = jsonify({'message': response})
            response.status_code = 200

        except Exception as e:
            # Incase of any errors handle them
            response = jsonify({'message': str(e)})
            print(f'Bucket selected {app.config["AUDIO_BUCKET"]}')
            response.status_code = 500
        
        # Finally respond to client with response 
        return response
    else:
        # if the file is not allowed then 
        resp = jsonify({'message' : f'Allowed file types are {",".join(ALLOWED_EXTENSIONS)}'})
        resp.status_code = 400
        return resp

if __name__ == "__main__":
    app.run(debug=True)