FROM python:3.6.5

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

COPY compose/django/pip.cache/ /tmp/pip.cache
ADD compose/django/requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt --cache-dir=/tmp/pip.cache

RUN rm -rf /tmp/pip.cache

RUN mkdir /app
WORKDIR /app

ADD bin/ /app/bin
ADD tritium/ /app/tritium
ADD scripts/ /app/scripts

ADD manage.py /app/
ADD wsgi.py /app/

COPY ./compose/django/*.sh /
RUN chmod +x /*.sh
ENTRYPOINT ["/entrypoint.sh"]
