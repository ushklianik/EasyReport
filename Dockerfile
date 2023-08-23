FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
ENV FLASK_APP=run.py
EXPOSE 7878
CMD ["flask", "run", "--host=0.0.0.0", "--port=7878"]