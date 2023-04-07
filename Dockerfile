FROM python:3

RUN pip install dnspython aiosmtpd pyspf dkimpy requests

EXPOSE 25

COPY main.py main.py

CMD [ "python","main.py" ]