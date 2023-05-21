FROM alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY ./images /images

COPY main.py main.py

RUN mkdir /db

RUN chown -R trainee:mercari /db

RUN chown -R trainee:mercari /images

USER trainee

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
# docker run -d -p 9000:9000 -v $(pwd)/db:/db build2023/app
# docker run -d -p 9000:9000 -v mercari_vol:/db -v $(pwd)/db/mercari.sqlite3:/db/mercari.sqlite3 build2023/app