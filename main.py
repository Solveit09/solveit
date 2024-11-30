from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app=FastAPI()
templates = Jinja2Templates(directory="public")

@app.get("/")
@app.get("/index")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

