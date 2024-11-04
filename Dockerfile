#FROM ubuntu:noble
FROM ubuntu:22.04

RUN apt-get update

RUN apt-get install -y python3 python3-pip

RUN pip3 install locust pandas

RUN mkdir /loadtester
WORKDIR /loadtester
ADD *.py .

RUN ls

EXPOSE 8089

ENV HOST="http://localhost"
ENV USERS="20"
ENV RATE="20.0"
ENV TIME="10m"
ENV CSV="results"

CMD locust -H $HOST -u $USERS -r $RATE -t $TIME --csv $CSV --autostart
