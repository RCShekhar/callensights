from flask import Flask, render_template, request, jsonify
import boto3

app = Flask(__name__)

# Configure AWS S3
s3_client = boto3.client('s3')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['file']

    # Check if file has a name
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    # Upload file to S3
    s3_client.upload_fileobj(file, 'your-s3-bucket-name', file.filename)

    return jsonify({'message': 'Upload successful'})

if __name__ == '__main__':
    app.run(debug=True)
