FROM python:3.9-alpine

RUN apk add --no-cache gcc musl-dev linux-headers

COPY . .

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

RUN python -m compileall /app

#RUN alembic upgrade head
