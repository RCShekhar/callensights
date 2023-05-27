from flask import Flask, render_template, request, redirect
from google.cloud import storage

app = Flask(__name__)

# Configure Google Cloud Storage
storage_client = storage.Client()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return redirect('/')

    file = request.files['file']

    # Check if file has a name
    if file.filename == '':
        return redirect('/')

    # Upload file to Google Cloud Storage
    bucket = storage_client.get_bucket('salesmaster')
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file)

    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
