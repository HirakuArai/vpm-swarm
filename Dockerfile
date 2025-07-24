FROM python:3.11-slim
WORKDIR /app
COPY main.py /app/
# Copy common modules for cells that need them (if they exist)
COPY ../common/ /app/common/ 2>/dev/null || echo "No common directory found"
RUN pip install fastapi uvicorn redis pydantic
CMD ["python", "main.py"]