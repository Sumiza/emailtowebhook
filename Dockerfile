FROM python:alpine

EXPOSE 25

ENV PYTHONUNBUFFERED=TRUE

RUN apk add --no-cache openssl
RUN pip install --upgrade pip
RUN pip install dnspython aiosmtpd pyspf dkimpy requests

COPY main.py main.py
COPY docker-entrypoint.sh docker-entrypoint.sh
COPY addons addons

ENTRYPOINT ["sh","docker-entrypoint.sh"]
CMD [ "python3","main.py" ]
