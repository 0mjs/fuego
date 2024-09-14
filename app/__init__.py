from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse

from app.service import Analyser

app = FastAPI()


@app.post("/analyse")
async def endpoint(file: UploadFile):
    return await Analyser(file).analyse()
