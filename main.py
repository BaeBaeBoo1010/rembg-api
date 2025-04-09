from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from rembg import remove
import io

app = FastAPI()

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    input_bytes = await file.read()
    if len(input_bytes) > 2 * 1024 * 1024:
        return {"error": "Image too large"}
    output_bytes = remove(input_bytes)
    return StreamingResponse(io.BytesIO(output_bytes), media_type="image/png")