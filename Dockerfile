FROM python:3 as memri-pyintegrators
ENV DEBIAN_FRONTEND=noninteractive

COPY ./integrators /usr/src/pyintegrators/integrators
COPY ./tools /usr/src/pyintegrators/tools
COPY ./MANIFEST.in /usr/src/pyintegrators/MANIFEST.in
COPY ./README.md /usr/src/pyintegrators/README.md
COPY ./settings.ini /usr/src/pyintegrators/settings.ini
COPY ./setup.py /usr/src/pyintegrators/setup.py
WORKDIR /usr/src/pyintegrators
RUN pip3 install --editable .
CMD ["python3", "tools/run_integrator.py"]
