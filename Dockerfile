FROM python:3-alpine
EXPOSE 5000
WORKDIR /app
COPY /app/requirements.txt requirements.txt

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev  && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

ENV FLASK_ENV=production
CMD flask run --host 0.0.0.0
