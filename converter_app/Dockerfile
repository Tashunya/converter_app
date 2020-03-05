FROM ubuntu:latest
MAINTAINER Tatiana Sakharova 'tashunya_17@mail.ru'
RUN apt-get update -y
RUN apt-get install -y python3-pip
COPY . /converter_app
WORKDIR /converter_app
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]