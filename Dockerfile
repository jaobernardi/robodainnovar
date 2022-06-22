# syntax=docker/dockerfile:1
FROM python:3.10.1-windowsservercore-ltsc2016
COPY . .
RUN pip install -r requirements.txt
RUN echo 'pull down choco'
RUN powershell -Command Install-PackageProvider -name chocolatey -Force
RUN powershell -Command Set-PackageSource -Name chocolatey -Trusted

RUN powershell -Command Get-PackageSource

RUN echo 'install chrome via choco'
RUN powershell -Command Install-Package GoogleChrome -MinimumVersion 74
CMD ["python3", "main.py"]