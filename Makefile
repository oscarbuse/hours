net:
	docker network create --subnet=172.18.0.0/16 hours-net	
bweb:
	cd hours-web; docker build -t example/hours-web .
rweb:
	docker run -d --rm --net hours-net --ip 172.18.0.3 -p 8080:8080 --name web example/hours-web
bdb:
	cd hours-db; docker build -t example/hours-db .
rdb:
	#docker run -d --rm --net hours-net --ip 172.18.0.2 --name db -v /var/lib/mysql:/var/lib/mysql example/hours-db
	docker run -d --rm --net hours-net --ip 172.18.0.2 --name db example/hours-db
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
