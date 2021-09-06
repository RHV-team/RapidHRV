FROM python:3.9

RUN pip install "poetry==1.1.7"
RUN poetry config virtualenvs.create false

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-interaction --no-ansi

COPY . /app