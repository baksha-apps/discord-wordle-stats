FROM python:3.8
WORKDIR /src
COPY . .
RUN ls
# Copies your code file from your action repository to the filesystem path `/` of the container
COPY entrypoint.sh /entrypoint.sh
CMD ["pip install -r requirements.txt --upgrade"]
RUN ["chmod", "+x", "/entrypoint.sh"]
# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
