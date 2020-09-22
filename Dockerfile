#FROM ubuntu:18.04
FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

# Install some basic utilities
#RUN apt-get update && apt-get install -y \
RUN apt-get -qq -y update
RUN apt-get -qq -y upgrade
RUN apt-get -qq -y install \
    ca-certificates \
    curl \
    sudo \
	&& rm -rf /var/lib/apt/lists/*


ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh
RUN bash Miniconda3-py37_4.8.2-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-py37_4.8.2-Linux-x86_64.sh
##ENV PATH=/miniconda/bin:${PATH}
#RUN conda update -y conda 
#RUN conda install pytorch torchvision -c pytorch
#RUN conda install -c conda-forge transformers
#RUN apt-get update && apt-get dist-upgrade
#RUN apt-get -y install --reinstall build-essential &&
#RUN conda install -c conda-forge pyemd

#RUN conda install -y python=3.7
RUN apt update && apt install python3-pip -y
RUN apt-get install build-essential libpoppler-cpp-dev pkg-config python3-dev -y

RUN pip3 install pdftotext
RUN pip3 install --upgrade pip
RUN python3 -m pip install -U pymupdf 
RUN pip3 install torch
RUN pip3 install transformers

