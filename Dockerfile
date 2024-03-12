FROM python:3.11

WORKDIR /app

COPY requirements.txt .
COPY poetry.lock .
COPY pyproject.toml .

RUN pip install -r requirements.txt
RUN poetry install --no-cache

COPY . .

RUN chmod +x .
ENV PYTHONPATH=/app

EXPOSE 80

CMD ["poetry", "run", "uvicorn", "app.application:application", "--host", "0.0.0.0", "--port", "80"]