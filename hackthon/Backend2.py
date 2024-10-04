from flask import Flask, request, render_template
import PyPDF2
import requests

app = Flask(__name__)

# API endpoint and API key for summarization
SUMMARIZATION_API_ENDPOINT = "https://api.meaningcloud.com/summarization-1.0"
API_KEY = "e1d13c80453c658e106061988090f038"

def extract_text_from_pdf(pdf_file):
    # Create a PyPDF2 reader object
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # Extract the text from the PDF
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def summarize_text(text):
    # Set the API request headers and payload
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'key': API_KEY,
        'txt': text,
        'sentences': 3  # Number of sentences to include in the summary
    }
    # Send the API request
    response = requests.post(SUMMARIZATION_API_ENDPOINT, headers=headers, data=payload)
    # Check if the API response was successful
    if response.status_code == 200:
        # Extract the summary from the API response
        response_json = response.json()
        if 'summary' in response_json:
            summary = response_json['summary']
        else:
            summary = "Failed to retrieve summary from API response."
    else:
        summary = "Failed to retrieve summary. API response status code: " + str(response.status_code)
    return summary

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', error=None, summary=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part', summary=None)
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error='No selected file', summary=None)
    if file and file.filename.endswith('.pdf'):
        text = extract_text_from_pdf(file)
        summary = summarize_text(text)
        return render_template('index.html', error=None, summary=summary)
    else:
        return render_template('index.html', error='Invalid file type', summary=None)

if __name__ == '__main__':
    app.run(debug=True)