FROM basereq:1.0

CMD ["flask", "db", "upgrade"]

CMD ["python", "manage.py", "server", "run"]
