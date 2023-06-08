from fastapi import FastAPI, Request
from request_get_my_stock import check_info_request, check_payment_request, get_articles
import uvicorn

app = FastAPI(debug=True)


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

@app.post('/check/')
async def root(request: Request):
    return 'OK'

@app.post('/article/')
async def root(request: Request):
    order_id = await request.json()['order_id']
    return get_articles(order_id)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)