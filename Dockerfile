FROM python:3.7 as memri-pyintegrators
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y libgl1-mesa-glx
WORKDIR /usr/src/pyintegrators

# In order to leverage docker caching, copy only the minimal
# information needed to install dependencies

COPY ./settings.ini ./settings.ini
COPY ./setup.py ./setup.py
RUN touch ./README.md

# Install dependencies

RUN python3 setup.py egg_info
RUN pip3 install -r integrators.egg-info/requires.txt

# Copy the real project-s sources (docker caching is broken from here onwards)

COPY ./MANIFEST.in ./MANIFEST.in
COPY ./README.md ./README.md
COPY ./tools ./tools
COPY ./integrators ./integrators
COPY ./nbs ./nbs
COPY ./test ./test

# Build the final image

RUN pip3 install --editable .
# CMD ["python3", "tools/run_integrator.py"]

