from io import BytesIO

from fastapi import FastAPI, HTTPException, Header, Request, UploadFile
from fastapi.params import Depends
from starlette import status
from fastapi.templating import Jinja2Templates
from py_pdf_parser.loaders import load
import resend

import ticket_parser as TicketParser

app = FastAPI()
templates = Jinja2Templates(directory="templates")
MAX_ALLOWED_FILE_LIMIT = 5_242_880  # 5MB


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


async def valid_content_length(
    content_length: int = Header(..., lt=MAX_ALLOWED_FILE_LIMIT)
):
    return content_length


@app.post("/send-email")
async def send_ticket_email(
    request: Request, file: UploadFile, file_size=Depends(valid_content_length)
):
    inmemory_file = BytesIO()
    for chunk in file.file:
        inmemory_file.write(chunk)
        if inmemory_file.tell() > MAX_ALLOWED_FILE_LIMIT:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

    inmemory_file.seek(0)
    print("starting file parse")
    try:
        document = load(inmemory_file)
    except Exception as error:
        print("Error loading file")
        # TODO - generic api error handler
        pass

    ticket = TicketParser.parse_ticket(document)

    resend.api_key = "<API>"

    r = resend.Emails.send({
    "from": "onboarding@resend.dev",
    "to": "anikait.makkar@outlook.com",
    "subject": "Hello World",
    "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
    })

    print(r)

    return "success"
