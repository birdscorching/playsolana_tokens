from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import calculate_tokens

app = FastAPI(title="PlaySolana Token Estimator")

class UserInput(BaseModel):
    wallet_address: str
    playdex_name: str

@app.post("/estimate")
def estimate_tokens(data: UserInput):
    try:
        # ⬇️ Вставь сюда свой расчёт:
        result = calculate_tokens(data.wallet_address, data.playdex_name)
        return {"wallet_address": data.wallet_address, "playdex_name": data.playdex_name, "estimated_tokens": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Welcome to PlaySolana Token Estimator API"}