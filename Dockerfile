FROM python:3.9.12-alpine3.15
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY . .
RUN apk add git nginx npm
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev
EXPOSE 80
EXPOSE 443
CMD sh /usr/src/app/runme.sh
