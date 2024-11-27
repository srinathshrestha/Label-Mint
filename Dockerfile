FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expose the port your application runs on
EXPOSE 8080

CMD ["python", "main.py"]
