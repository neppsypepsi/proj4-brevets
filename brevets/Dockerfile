FROM python:3.13-slim
LABEL maintainer="Nigel Epperson"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["flask_brevets.py"]
