FROM python:latest
LABEL maintainer="Derek Merck <derek.merck@ufl.edu>"
RUN apt update \
 && DEBIAN_FRONTEND=noninteractive apt install -y -q nano \
 && rm -rf /var/lib/apt/lists/*

# This installs the package in user mode
# RUN pip install git+https://github.com/derekmerck/diana3

# This installs the package in developer mode, for easier local updates,
# editing of scripts, etc.
RUN git clone --recurse-submodules https://github.com/derekmerck/diana3 /opt/diana
# For developer/editable installations, need to install the submodule separately (!)
RUN pip install -e /opt/diana/libsvc /opt/diana

# Test that it works
#RUN diana-cli --version

CMD tail -f /dev/null