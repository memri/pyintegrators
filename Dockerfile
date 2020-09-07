FROM ubuntu:latest as memri-pyintegrators
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y python3-pip

COPY ./ /usr/src/pyintegrators
WORKDIR /usr/src/pyintegrators
RUN pip3 install --editable .
CMD ["python3", "tools/run_integrator.py"]
