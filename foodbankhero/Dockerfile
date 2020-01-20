FROM python:3.8

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

# The app source code is currently mounted via a volume into /app on the container.
# If you remove the volume, comment in the following line to bake the source code into the image.
# ADD . /app

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0"]
