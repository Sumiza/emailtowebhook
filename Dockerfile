FROM python:alpine


RUN pip install --upgrade pip
RUN pip install dnspython aiosmtpd pyspf dkimpy requests

EXPOSE 25

COPY main.py main.py

CMD [ "python3","main.py" ]