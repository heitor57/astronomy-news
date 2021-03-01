# Usage instructions
## Splash
				
				pip install scrapy-splash
				docker pull scrapinghub/splash
				docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash

## Scrapy

				pip install scrapy

## MongoDB Docker 

				# docker service on...
				systemctl start docker
				docker pull mongo
				docker run --name main-mongo -d mongo:latest
				# Help commands
				docker exec -it main-mongo mongo news_crawler --eval "db.dropDatabase()"
