FROM mysql:latest
MAINTAINER Oscar Buse <oscar@kwalinux.nl>
USER root

ENV MYSQL_ROOT_PASSWORD 'changeme'
ENV MYSQL_DATABASE accounting
ENV MYSQL_USER 'alice'
ENV MYSQL_PASSWORD 'changeme'

RUN apt-get update
RUN apt-get -y install vim net-tools

# table "hours"
COPY hours.sql /docker-entrypoint-initdb.d
