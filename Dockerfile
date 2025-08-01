FROM ubuntu:latest
LABEL authors="urielrodriguez"

ENTRYPOINT ["top", "-b"]