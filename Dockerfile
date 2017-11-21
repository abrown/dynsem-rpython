FROM fedora:latest

RUN dnf install gcc python3 findutils -y
RUN dnf clean all
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /home/dynsem
COPY 3rd 3rd
COPY src src
COPY Makefile .

CMD bash
