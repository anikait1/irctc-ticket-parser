from datetime import datetime
from io import BytesIO
from pprint import pprint
from flask import Flask, render_template, request
import os

from py_pdf_parser.loaders import load_file, PDFDocument, load
import ticket_parser as TicketParser


app = Flask(__name__)
MAX_ALLOWED_FILE_LIMIT = 5_242_880 # 5MB

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    file_size = 0
    a = BytesIO()
    for chunk in file.stream:
        file_size += len(chunk)
        if file_size > MAX_ALLOWED_FILE_LIMIT:
            return 'error'
        
        a.write(chunk)

    a.seek(0)


    now = datetime.now()
    document = load(a)
    ticket = TicketParser.parse_ticket(document)
    end = datetime.now()
    pprint(ticket)


    return f'{(end - now).microseconds / 1000}'





