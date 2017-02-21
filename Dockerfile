FROM ubuntu

RUN apt-get update
RUN apt-get install -y python python-pip build-essential libssl-dev libffi-dev python-dev

WORKDIR /app

ADD ./ /app

RUN pip install -r ./requirements.txt

CMD python run.py
