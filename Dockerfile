FROM python:3.10-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ADD Pipfile* ./
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir httpie pipenv
RUN pipenv install --system --deploy --ignore-pipfile

ADD . .

ENTRYPOINT ["python3"]
CMD ["main.py"]
