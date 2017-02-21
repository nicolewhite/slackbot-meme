FROM ubuntu

RUN apt-get update
RUN apt-get install -y python
RUN apt-get install -y python-pip

RUN pip install requests
RUN pip install flask

WORKDIR /app

ADD ./ /app

CMD python run.py
