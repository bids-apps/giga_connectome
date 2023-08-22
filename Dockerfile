FROM python:3.9

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
        git && \
    rm -rf /var/lib/apt/lists/*

ARG TEMPLATEFLOW_HOME="/templateflow"

RUN mkdir -p /templateflow

COPY [".", "/code"]

RUN pip install --upgrade pip && pip3 install -e .

WORKDIR /code

RUN python3 -c "from templateflow.api import get; get(['MNI152NLin2009cAsym', 'MNI152NLin6Asym'])"

ENV TEMPLATEFLOW_HOME=${TEMPLATEFLOW_HOME}

RUN git submodule update --init --recursive && python3 tools/download_templates.py

ENTRYPOINT ["/usr/local/bin/giga_connectome"]
