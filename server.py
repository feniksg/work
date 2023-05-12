from fastapi import FastAPI, Request
from request_get_my_stock import check_info_request
import uvicorn

app = FastAPI(debug=True)


@app.post("/create")
async def root(request: Request):
    data = await request.json()
    return check_info_request(data)


@app.post("/update")
async def root(request: Request):
    data = await request.json()
    return check_info_request(data)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)