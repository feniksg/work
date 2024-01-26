from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from request_get_my_stock import check_info_request, check_payment_request, get_articles, calc_additional_data_product
import uvicorn, sys,traceback
from tgbot import send_alert_message
app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create/")
async def root(request: Request):
    data = await request.json()
    return check_info_request(data["events"][0]["meta"]["href"])

@app.post("/update/")
async def root(request: Request):
    data = await request.json()
    return check_info_request(data["events"][0]["meta"]["href"])

@app.post('/payment/')
async def root(request: Request):
    data = await request.json()
    return check_payment_request(data["events"][0]["meta"]["href"])

@app.post('/itemcreate/')
async def root(request: Request):
    data = await request.json()
    return calc_additional_data_product(data["events"][0]["meta"]["href"])

@app.post('/itemupdate/')
async def root(request: Request):
    data = await request.json()
    return calc_additional_data_product(data["events"][0]["meta"]["href"])

@app.get('/check/')
async def root(request: Request):
    return 'OK'

@app.get('/article/')
async def root(ordnum):
    return get_articles(ordnum)

if __name__ == "__main__":
    try:
        uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_str = ''.join(traceback.format_tb(exc_traceback))
        error_info = f"Exception Type: {exc_type.__name__}\nException Value: {exc_value}\nModule: {sys.argv[0]}\nTraceback: {traceback_str}"
        send_alert_message(error_info)