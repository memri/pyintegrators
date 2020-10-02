FROM python:3 as memri-pyintegrators
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y libgl1-mesa-glx

# In order to leverage docker caching, copy only the minimal
# information needed to install dependencies

COPY ./settings.ini /usr/src/pyintegrators/settings.ini
COPY ./setup.py /usr/src/pyintegrators/setup.py
RUN touch /usr/src/pyintegrators/README.md

# Install dependencies

WORKDIR /usr/src/pyintegrators
RUN python3 setup.py egg_info
RUN pip3 install -r integrators.egg-info/requires.txt

# Copy the real project-s sources (docker caching is broken from here onwards)

COPY ./MANIFEST.in /usr/src/pyintegrators/MANIFEST.in
COPY ./README.md /usr/src/pyintegrators/README.md
COPY ./tools /usr/src/pyintegrators/tools
COPY ./integrators /usr/src/pyintegrators/integrators

# Build the final image

RUN pip3 install --editable .
CMD ["python3", "tools/run_integrator.py"]

