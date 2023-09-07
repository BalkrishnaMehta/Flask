FROM python:3.12-rc-slim

WORKDIR /app

RUN pip3 install flask
RUN pip3 install flask_restful
RUN pip3 install pymongo
RUN pip3 install Werkzeug

COPY . /app/

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]



