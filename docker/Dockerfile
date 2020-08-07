FROM python:latest
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y -q nano
RUN git clone --recurse-submodules https://github.com/derekmerck/diana3 /opt/diana
# For editable installs, need to install them separately
RUN pip install -e /opt/diana/libsvc /opt/diana

RUN diana-cli --version
