FROM python:3 as memri-pyintegrators
ENV DEBIAN_FRONTEND=noninteractive

COPY ./ /usr/src/pyintegrators
WORKDIR /usr/src/pyintegrators
RUN pip3 install --editable .
CMD ["python3", "tools/run_integrator.py"]
