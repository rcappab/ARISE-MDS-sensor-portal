@echo on
docker-compose stop
docker-compose build sensor_portal_django
cmd /k docker-compose -f docker-compose-dev.yml up