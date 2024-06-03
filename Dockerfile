# https://hub.docker.com/layers/library/python/3.12.3-slim-bullseye/images/sha256-11ee4eb9e164c0ff4aeb4eef37163aedc358f57045f394f719b8c130190a440d
FROM python@sha256:6fa552fb879325884b0c1b6792d14ae9500d246c8b19cc27876d84c7c41117ff

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
