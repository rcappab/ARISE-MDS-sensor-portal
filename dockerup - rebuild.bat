@echo on
docker-compose -f docker-compose-dev.yml stop
docker-compose -f docker-compose-dev.yml build
cmd /k docker-compose -f docker-compose-dev.yml up