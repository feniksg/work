from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from request_get_my_stock import check_info_request, check_payment_request, get_articles, calc_additional_data_product
import uvicorn

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
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)