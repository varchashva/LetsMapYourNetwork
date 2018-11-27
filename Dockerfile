# base image
FROM ubuntu:18.04

# working directory
WORKDIR /root/LMYN

# Install Nmap
RUN apt-get update -y && apt-get install -y nmap

# Install CURL
RUN apt-get install -y curl

# Install python2.7
RUN apt-get install -y python2.7

# Copy the entire code to working directory
COPY . /root/LMYN

# Install pre-requisites
RUN apt install -y python-pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 9999
CMD ["python","manage.py","runserver","0.0.0.0:9999"]