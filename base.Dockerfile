FROM python:3.9-slim

COPY . .

RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

RUN python -m compileall /app
