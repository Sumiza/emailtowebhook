#!/bin/sh

if [ -n "$PIP_INSTALL" ]
then
    pip install --upgrade pip
    for i in $PIP_INSTALL
        do
            pip install "$i"
        done
fi

if [ -n "$BUILTIN_ADDON" ]
then
    cp /addons/$BUILTIN_ADDON/addon.py .
fi

if [ -n "$TLS_CERT_HOST" ]
then
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 3000 -nodes -subj "/CN=$TLS_CERT_HOST" 2>/dev/null
fi

if [ -n "$DOWNLOAD_ADDON" ]
then
    wget -O addon.py $DOWNLOAD_ADDON
fi

exec "$@"
