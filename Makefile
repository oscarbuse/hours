net:
	docker network create --subnet=172.18.0.0/16 hours-net	
bweb:
	cd hours-web; docker build -t oscarbuse/hours-web .
rweb:
	docker run -d --net hours-net --ip 172.18.0.3 -p 8080:8080 --name web oscarbuse/hours-web

bweb2:
	cd hours-web; docker build -t example/hours-web2 .
rweb2:
	docker run -d --net hours-net --ip 172.18.0.4 -p 8020:80 --name web2 example/hours-web2

bdb:
	cd hours-db; docker build -t example/hours-db .

#docker run -d --net hours-net --ip 172.18.0.2 --name db example/hours-db
#docker run -dit -P --name web -v /var/stack/docker/d1:/web1:z changed-ubuntu bash
#docker run -d --net hours-net --ip 172.18.0.2 --name db -v /root/docker/hours/hours-db/data/accounting:/var/lib/mysql/accounting example/hours-db
rdb:
	docker run -d --net hours-net --ip 172.18.0.2 --name db -v /var/lib/mysql:/var/lib/mysql example/hours-db

ball:	bweb bdb
rall:	rweb rdb
all:	net bweb bdb rweb rdb
stop:
	docker stop $$(docker ps -q)
rm:
	docker rm web db
clean:
	docker rm $$(docker ps -a -q); docker rmi $$(docker images | grep "^<none>" | awk "{print $$3}")
cleanall: clean
	docker network rm hours-net;
