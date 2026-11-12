# https://hub.docker.com/_/python/tags?name=3.14.10-slim-trixie
FROM python:3.14.10-slim-trixie@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f

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
# Ignore packages in the user site directory (e.g. ~/.local/lib/pythonX.Y/site-packages).
ENV PYTHONNOUSERSITE=1

RUN git submodule update --init --recursive && python3 /code/tools/download_templates.py

ENTRYPOINT ["/usr/local/bin/giga_connectome"]
