FROM httpd:2.4
MAINTAINER Oscar Buse <oscar@kwalinux.nl>
RUN useradd -c 'Oscar' -m -d /home/oscar -s /bin/bash oscar

RUN apt-get update
# libdbd-mysql-perl also gets DBI.pm
RUN apt-get -y install vim libcgi-pm-perl libdbd-mysql-perl net-tools lsof
RUN apt-get -y install libdatetime-format-strptime-perl libdate-calc-perl
RUN mkdir -p /usr/local/apache2/libs

# Application Code
COPY index.* /usr/local/apache2/htdocs/
COPY *.pm /usr/local/apache2/libs/
COPY httpd.conf /usr/local/apache2/conf

RUN chown oscar /usr/local/apache2/logs
USER oscar
