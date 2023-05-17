FROM alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY main.py main.py

COPY /db/mercari.sqlite3 /db/mercari.sqlite3

RUN chown -R trainee:mercari /db

VOLUME /db

USER trainee

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
# docker run -d -p 9000:9000 -v $(pwd)/db:/db build2022/app