FROM python:latest
LABEL maintainer="Oliver Epper <oliver.epper@gmail.com>"

RUN useradd -ms /home/logbuch logbuch
WORKDIR /home/logbuch

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip && \
    venv/bin/pip install -r requirements.txt && \
    venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY run.py config.py boot.sh ./
RUN mkdir instance && \
    chmod a+x boot.sh

ENV FLASK_APP run.py

RUN chown -R logbuch:logbuch ./
USER logbuch

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
