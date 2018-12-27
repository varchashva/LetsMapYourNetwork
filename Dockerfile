# base image
FROM ubuntu:18.04

# working directory
WORKDIR /root/LMYN

# Install pre-requisites
RUN apt-get update -y && apt-get install -y nmap curl python2.7 python-pip python-setuptools --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy the entire code to working directory
COPY . /root/LMYN

# Install requirements.txt from pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 9999
CMD ["python","manage.py","runserver","0.0.0.0:9999"]