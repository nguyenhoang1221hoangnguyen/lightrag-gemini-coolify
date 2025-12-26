import os
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lightrag import LightRAG, QueryParam
import google.generativeai as genai

# 1. Cấu hình Gemini
# Lấy API Key từ biến môi trường (sẽ cài trong Coolify)
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

# 2. Định nghĩa hàm Wrapper cho Gemini để LightRAG hiểu
async def gemini_model_complete(prompt, system_prompt=None, history_messages=[], **kwargs) -> str:
    # Chọn model (Flash cho nhanh và rẻ, hoặc Pro cho thông minh)
    model = genai.GenerativeModel('gemini-1.5-flash') 
    
    # Ghép system prompt vào prompt (vì Gemini API python xử lý hơi khác)
    full_prompt = ""
    if system_prompt:
        full_prompt += f"System: {system_prompt}\n"
    full_prompt += f"User: {prompt}"
    
    response = model.generate_content(full_prompt)
    return response.text

async def gemini_embedding(texts: list[str]) -> np.ndarray:
    # Dùng model embedding của Google
    model = "models/text-embedding-004"
    results = []
    for text in texts:
        # Google embedding từng cái hoặc batch nhỏ
        embedding = genai.embed_content(model=model, content=text, task_type="retrieval_document")
        results.append(embedding['embedding'])
    return np.array(results)

# 3. Khởi tạo LightRAG
WORKING_DIR = "/app/data"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=gemini_model_complete,  # Trỏ vào hàm Gemini viết ở trên
    embedding_func=gemini_embedding        # Trỏ vào hàm Embedding Gemini
)

# 4. Tạo API FastAPI
app = FastAPI()

class TextData(BaseModel):
    text: str

class QueryData(BaseModel):
    query: str
    mode: str = "hybrid" # local, global, hybrid, mix

@app.post("/insert")
async def insert_text(data: TextData):
    try:
        rag.insert(data.text)
        return {"status": "success", "message": "Text inserted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_rag(data: QueryData):
    try:
        result = rag.query(data.query, param=QueryParam(mode=data.mode))
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "backend": "Gemini"}