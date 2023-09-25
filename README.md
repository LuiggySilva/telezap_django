# FILE STRUCTURE
> ```
> .  
> ├── app/ 
> │   ├── apps/
> │   │   ├── chat/
> │   │   ├── group_chat/
> │   │   ├── notification/
> │   │   ├── user/
> │   │   ├── videocall/
> │   │   └── util.py
> │   ├── docs/  
> │   ├── mediafiles/  
> │   ├── staticfiles/  
> │   ├── telezap_django/  
> │   ├── templates/  
> │   ├── db.sqlite3  
> │   ├── Dockerfile  
> │   ├── Dockerfile.prod  
> │   ├── entrypoint.prod.sh  
> │   ├── entrypoint.sh  
> │   ├── manage.py  
> │   └── requirements.txt  
> ├── ngix/  
> │   ├── Dockerfile  
> │   └── nginx.conf  
> ├── venv/  
> ├── docker-compose.prod.yml  
> ├── docker-compose.yml  
> ├── .dockerignore  
> ├── .env  
> ├── .env.prod  
> ├── .env.prod.db  
> ├── .gitignore  
> └── README.md  
> ```

<br><br>

# RUN PROJECT

## *.env* to DEV mode
> ```js
> DEBUG = `True`
> SECRET_KEY = `<string>`
> DJANGO_ALLOWED_HOSTS = `localhost 127.0.0.1 [::1]`
> ```

## *.env.prod* to PROD mode
> ```js
> DEBUG = `False` 
> SECRET_KEY = `<string>`
> DJANGO_ALLOWED_HOSTS = `<string_list>`
> SQL_ENGINE = `django.db.backends.postgresql`
> SQL_DATABASE = `<string: database name>`
> SQL_USER = `<string>`
> SQL_PASSWORD = `<string>`
> SQL_HOST = `db`
> SQL_PORT = `5432`
> DATABASE = `postgres`
> ```


## *.env.prod.db* to PROD mode
> ```js
> POSTGRES_USER = `<string: equals to .env.prod SQL_USER>`
> POSTGRES_PASSWORD = `<string: equals to .env.prod SQL_PASSWORD>`
> POSTGRES_DB = `<string: equals to .env.prod SQL_DATABASE>` 
> ```


## Run project without Docker in DEV mode
> 1. **RUN** `python -m venv venv`
> 2. **RUN** *Windowns:* `venv/bin/activate.bat` | *Linux:* `source venv/bin/activate`
> 3. **RUN** `pip install -r requirements.txt`
> 4. **RUN** `python ./app/manage.py migrate`
> 5. **RUN** `python ./app/manage.py runserver`
> 6. Go to [http://localhost:8000](http://localhost:8000) in browser

<br>

## Run project with Docker in DEV mode
> 1. **RUN** `docker-compose up -d --build`
> 2. Go to [http://localhost:8000](http://localhost:8000) in browser

<br>

## Run project with Docker in PROD mode
> 1. **RUN** `docker-compose -f docker-compose.prod.yml up -d --build`
> 2. Go to [http://localhost:1337](http://localhost:1337) in browser

<br>

## Run BASH in project container
> - **RUN** `docker exec -it telezap_django-web-1 bash`

<br>

## Stop and Remove all project Docker files
> 1. **RUN** `docker container stop telezap_django-web-1`
> 2. **RUN** `docker container stop telezap_django-db-1` ***(IF RUN IN PROD)***
> 3. **RUN** `docker rm telezap_django-web-1`
> 4. **RUN** `docker rm telezap_django-db-1` ***(IF RUN IN PROD)***
> 5. **RUN** `docker rmi telezap_django-web`
> 6. **RUN** `docker volume remove telezap_django_postgres_data` ***(IF RUN IN PROD)***
> 7. **RUN** `docker network remove telezap_django_default`

<br><br>

# RUN PROJECT TESTS

## Run all tests
> - **RUN** `python manage.py test apps/*/`

## Run single app tests
> - **RUN** `python manage.py test apps/<app_name>/`  
> ***APPS NAMES:*** user | notification | chat | group_chat | videocall
