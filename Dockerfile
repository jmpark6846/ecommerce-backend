FROM python:3.8
ENV PYTHONUNBUFFERED=1
COPY Pipfile /app/
COPY Pipfile.lock /app/

WORKDIR /app

RUN pip3 install pipenv
RUN pipenv install --ignore-pipfile --system --deploy
EXPOSE 8000