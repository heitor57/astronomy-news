# :telescope::newspaper: Astronomy News

This repository contains a news crawler project that uses data mining approaches, including text mining, to make analyses in combination with an amazing data visualization with the purpose of centralize astronomy news.

## Usage instructions
### Splash
				
	pip install scrapy-splash
	docker pull scrapinghub/splash
	docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash

### Scrapy

	pip install scrapy
	python -mscrapy crawl ig -s JOBDIR=crawls/ig

### MongoDB Docker 

	# docker service on...
	systemctl start docker
	docker pull mongo
	docker run --name main-mongo -d mongo:latest
	# Help commands
	docker exec -it main-mongo mongo news_crawler --eval "db.dropDatabase()"
