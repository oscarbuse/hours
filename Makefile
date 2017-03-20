net:
	docker network create --subnet=172.18.0.0/16 hours-net	
bweb:
	cd hours-web; docker build -t example/hours-web .
rweb:
	docker run -d --net hours-net --ip 172.18.0.3 -p 8080:80 example/hours-web
bdb:
	cd hours-db; docker build -t example/hours-web .
rdb:
	docker run -d --net hours-net --ip 172.18.0.2 example/hours-db
rall:	rweb rdb
all:	net bweb bdb rweb rdb
clean:
	docker rm $$(docker ps -a -q); docker rmi $$(docker images | grep "^<none>" | awk "{print $$3}")
cleanall: clean
	docker network rm hours-net;
