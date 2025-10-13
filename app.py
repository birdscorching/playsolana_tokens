import threading
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from utils import calculate_tokens, get_signs_dict



app = FastAPI(
    title="PlaySolana Token Estimator",
    description="API и веб-форма для расчёта количества токенов PlaySolana",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")


class UserInput(BaseModel):
    wallet_address: str
    playdex_name: str

@app.on_event("startup")
def preload_signatures():
    # выполняется в фоне при запуске API
    threading.Thread(target=get_signs_dict, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "result": None})


@app.post("/", response_class=HTMLResponse)
async def estimate_form(
    request: Request,
    wallet_address: str = Form(...),
    playdex_name: str = Form(...)
):
    try:
        result = calculate_tokens(wallet_address, playdex_name)
        return templates.TemplateResponse("form.html", {"request": request, "result": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/estimate")
def estimate_api(data: UserInput):
    try:
        result = calculate_tokens(data.wallet_address, data.playdex_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)