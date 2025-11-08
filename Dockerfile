# Use Python 3.7 as specified in the original README
FROM python:3.7-slim

WORKDIR /app

# Requirements layer. Won't be rebuilt
# every time the code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Don't buffer output (so logs appear immediately)
ENV PYTHONUNBUFFERED=1

VOLUME ["/app/output"]

CMD ["python", "entrypoint.py"]

