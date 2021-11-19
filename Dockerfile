FROM python:3.5
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install -y python3-opencv
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]
