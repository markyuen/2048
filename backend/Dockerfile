FROM python:3.14.2-alpine

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /code/app
ARG PORT=8000
ENV PORT=$PORT
CMD fastapi run app/api.py --port $PORT
