# https://hub.docker.com/_/python/tags?name=3.14.9-slim-trixie
FROM python:3.14.9-slim-trixie@sha256:35caba83af2fe6da9a5d922f9b0156f21d1246a48278c58a08bd253303ba42e8

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
        git && \
    rm -rf /var/lib/apt/lists/*

ARG TEMPLATEFLOW_HOME="/templateflow"

WORKDIR /code

COPY [".", "/code"]

RUN pip3 install --no-cache-dir pip==24.0 && \
    pip3 install --no-cache-dir --requirement requirements.txt && \
    pip3 --no-cache-dir install .

ENV TEMPLATEFLOW_HOME=${TEMPLATEFLOW_HOME}

RUN git submodule update --init --recursive && python3 /code/tools/download_templates.py

ENTRYPOINT ["/usr/local/bin/giga_connectome"]
