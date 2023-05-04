FROM python:3.9

ARG DEBIAN_FRONTEND="noninteractive"

RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
        git && \
    rm -rf /var/lib/apt/lists/*

ARG TEMPLATEFLOW_HOME="/templateflow"

RUN pip3 install nilearn==0.9.2 templateflow pybids h5py tqdm&& \
    mkdir -p /code && mkdir -p /templateflow

WORKDIR /code

RUN python3 -c "from templateflow.api import get; get(['MNI152NLin2009cAsym', 'MNI152NLin6Asym'])"

COPY [".", "/code"]

RUN pip install --upgrade pip && pip3 install -e .

ENV TEMPLATEFLOW_HOME=${TEMPLATEFLOW_HOME}

ENTRYPOINT ["/usr/local/bin/giga_connectome"]
