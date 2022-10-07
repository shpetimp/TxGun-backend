FROM python:3.6.5

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

RUN mkdir /build
WORKDIR /build

ADD ./requirements.txt /build/
ADD ./pip.cache/ /tmp/pip.cache

RUN pip install -r /build/requirements.txt --cache-dir=/tmp/pip.cache

RUN rm -rf /tmp/pip.cache

RUN mkdir /app
WORKDIR /app

COPY ./*.sh /
RUN chmod +x /*.sh

ENTRYPOINT ["/entrypoint.sh"]

