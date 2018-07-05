FROM python:3.6.5-alpine3.7

WORKDIR /usr/src/project

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
                                                                                                                                                                                               
CMD ["gunicorn", "-b", "0.0.0.0:8080", "bot:app"]
