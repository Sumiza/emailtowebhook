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
    mv /addons/$BUILTIN_ADDON/addon.py .
fi

exec "$@"
