# syntax=docker/dockerfile:1
FROM python:3.10.5-bullseye
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt update -y
RUN apt install -y google-chrome-stable
COPY . .
CMD ["python3", "main.py"]