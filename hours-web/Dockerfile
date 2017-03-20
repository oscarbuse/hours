FROM httpd:latest
MAINTAINER Oscar Buse <oscar@kwalinux.nl>
USER root

#ENV AP /var/www/hours/web-docs
RUN apt-get update
# libdbd-mysql-perl also gets DBI.pm
RUN apt-get -y install vim libcgi-pm-perl libdbd-mysql-perl
RUN apt-get -y install libdatetime-format-strptime-perl libdate-calc-perl
RUN mkdir -p /usr/local/apache2/libs

# Application Code
COPY index.* /usr/local/apache2/htdocs/
COPY *.pm /usr/local/apache2/libs/
COPY httpd.conf /usr/local/apache2/conf
#ADD * $AP/

#WORKDIR $AP
#CMD /usr/local/bin/node /data/app/index.js
