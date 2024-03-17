from datetime import datetime
import gc
from io import BytesIO
import os
from pprint import pprint
import random
from tempfile import NamedTemporaryFile
from typing import BinaryIO

from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from starlette import status
from fastapi.templating import Jinja2Templates
from py_pdf_parser.loaders import load_file, PDFDocument, load


import ticket_parser as TicketParser

app = FastAPI()
# templates = Jinja2Templates(directory="templates")
MAX_ALLOWED_FILE_LIMIT = 5_242_880 # 5MB


# @app.get("/")
# async def index(request: Request):
#     return templates.TemplateResponse(request=request, name="index.html")

@app.post("/send-email")
async def send_ticket_email(request: Request, file: UploadFile):
    # file.file.seek(0, os.SEEK_END)
    file_size = 0

    a = BytesIO()
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > MAX_ALLOWED_FILE_LIMIT:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        a.write(chunk)
    
    a.seek(0)
    
    now = datetime.now()
    document = load(a)
    ticket = TicketParser.parse_ticket(document)
    end = datetime.now()
    pprint(ticket)


    return f'{(end - now).microseconds / 1000}'
