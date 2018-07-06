FROM python:3.6.5-alpine3.7

WORKDIR /usr/src/project

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG PORT=5000

ENV PORT ${PORT}
                                                                                                                                                                                               
CMD ["sh", "-c", "gunicorn -b '0.0.0.0:$PORT' bot:app"]
