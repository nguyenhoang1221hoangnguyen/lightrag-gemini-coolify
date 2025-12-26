FROM python:3.10-slim

WORKDIR /app

# Cài đặt các thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy mã nguồn
COPY . .

# Expose cổng 8000
EXPOSE 8000

# Chạy app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]