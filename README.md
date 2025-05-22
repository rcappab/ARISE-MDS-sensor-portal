# ARISE-MDS sensor portal
 
This is a shareable version of the ARISE-MDS sensor portal. It is currently a work in progress. This documentation will be updated when the code approaches a release. Please note this branch is very much a WIP, and there may be a risk of breaking changes occasionally.

## Starting the project for the first time

The system expects environmental variables to be present in a .env file. 

TODO: LIST REQUIRED ENV VARS FOR DEVELOPMENT AND PRODUCTION

```bash
docker compose -f docker-compose-dev.yml build
```

```bash
docker compose -f docker-compose-dev.yml up
```

### Init database & super user:

```bash
docker compose -f docker-compose-dev.yml exec sensor_portal_django python manage.py migrate
```

```bash
docker compose -f docker-compose-dev.yml exec sensor_portal_django python manage.py createsuperuser
```


## Populating with dummy data
```bash
docker compose -f docker-compose-dev.yml exec sensor_portal_django bash
```

```bash
python manage.py shell
```

```py
from data_models import factories

factories.DeploymentFactory()
```

## Testing
```bash
docker compose -f docker-compose-dev.yml exec sensor_portal_django pytest
```
