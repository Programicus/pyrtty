FROM mcr.microsoft.com/devcontainers/python:3
RUN sudo apt update \
	&& sudo apt upgrade \
	&& sudo apt -y install libportaudio2 cmake libopenblas-dev gfortran
COPY requirements.txt /temp/
RUN pip install -r /temp/requirements.txt
RUN rm /temp/requirements.txt