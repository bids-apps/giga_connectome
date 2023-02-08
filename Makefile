# Makefile that defines simple testing

all: test-python

get_data:
	if [ ! -d data/ds000114_R2.0.1 ]; then wget -c -O ds000114_reduced_with_derivatives.zip "https://osf.io/download/yx32y/" && mkdir -p data && unzip ds000114_reduced_with_derivatives.zip -d data && rm ds000114_reduced_with_derivatives.zip; fi

test-python: get_data
	pytest --cov=giga_connectome giga_connectome/tests/

# build-docker: Dockerfile main.py run.py
# 	python -c "import main; main.copy_atlas()"
# 	docker build -t bids/rs_signal_extract .

# run-interative:
# 	docker run -it --entrypoint /bin/bash -v $(shell pwd)/data:/data -v $(shell pwd)/docker_outputs:/outputs bids/rs_signal_extract

# test-docker: get_data
# 	-mkdir -p docker_outputs
# 	docker run -v $(shell pwd)/data:/data -v $(shell pwd)/docker_outputs:/outputs bids/rs_signal_extract /data/ds000114_R2.0.1/derivatives/fmriprep /outputs group
