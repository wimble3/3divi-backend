FROM basereq:1.0

RUN apk add --no-cache gcc musl-dev linux-headers

#RUN alembic upgrade head

CMD ["python", "manage.py", "server", "run"]
