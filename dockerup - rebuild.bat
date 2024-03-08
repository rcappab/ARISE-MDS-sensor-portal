@echo on
docker-compose stop
docker-compose build webservice
cmd /k docker-compose -f docker-compose-dev.yml up