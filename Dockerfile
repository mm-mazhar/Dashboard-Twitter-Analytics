FROM python:3.8-slim-buster

RUN mkdir wd
WORKDIR wd
<<<<<<< HEAD
COPY ./requirements.txt ./
=======
COPY ./requirements.txt .
>>>>>>> 0421c7593a13f21beeee7a508d7c5cfadb1d96d1
RUN pip3 install -r requirements.txt

COPY ./ ./

CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:80", "appTabs:server"]
