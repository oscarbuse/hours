# hour registration
This is a (very) simple app to demonstrate the use of two docker containers in their own subnet ("hours-net").
The app itself can be used (with tweaking..) to keep track of working hours.
The containers:
* docker hours-web: runs apache and has the index.cgi in /usr/local/apache2/htdocs/
* docker hours-db: runs mysql and has the database "accounting" with the table "hours".
# Note:
After running "make all" you need to enter the container "hours-db" (with docker exec -it "Container ID" /bin/bash) and run /root/create_table_hours.sh
(I can't get this working from the docker host at the moment..)
