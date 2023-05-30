# Start with a base image
FROM ubuntu:latest

SHELL ["/bin/bash", "-c"]

# Install necessary packages
RUN apt-get update && \
    apt-get install -y build-essential wget manpages-dev && \
    apt-get install -y gcc-12 g++-12 gcc-11 g++-11 gcc-10 g++-10 gcc-9 g++-9 && \
    apt-get install -y python3

# Set environment variables
ENV PATH="/usr/local/bin:${PATH}"
