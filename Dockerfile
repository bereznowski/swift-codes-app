FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src

COPY ./data/swift_codes.xlsx /code/data/swift_codes.xlsx

CMD ["fastapi", "run", "src/app.py", "--port", "8000"]