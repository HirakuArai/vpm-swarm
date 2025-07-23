FROM python:3.11-slim
WORKDIR /app
COPY main.py /app/
RUN pip install fastapi uvicorn
CMD ["python", "main.py"]