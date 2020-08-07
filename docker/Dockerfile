FROM python:latest
MAINTAINER Derek Merck
RUN apt update \
 && DEBIAN_FRONTEND=noninteractive apt install -y -q nano python3-numpy \
 && rm -rf /var/lib/apt/lists/*
RUN git clone --recurse-submodules https://github.com/derekmerck/diana3 /opt/diana
# For developer/editable installations, need to install the submodule separately (!)
RUN pip install -e /opt/diana/libsvc /opt/diana

#RUN diana-cli --version
