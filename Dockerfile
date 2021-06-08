# Use Python image.
FROM python:3

# Copy local code to the container image.
ENV APPHOME /app
COPY requirements.txt $APPHOME/requirements.txt
WORKDIR $APPHOME
RUN pip3 install -r requirements.txt
COPY . $APPHOME
ENTRYPOINT ["gunicorn"]
CMD ["-b",":8080","main:app"]
