# flaskit

- create virtual env

	`virtualenv --python python3.6 env`
	
- activate virtual env

	`source env/bin/activate`
	
- install dependencies and use config for postgresql in dev mode

	`make install && make dev_pg`
	
- set up database environment variables

	`source script/dev.sh`
	
- drop all tables

	`python manage.py drop_db`

- create all tables

	`python manage.py init_db`
	
- insert scaffolding data

	`python manage.py init_data`
	
- run the application.

	`flask run --host 0.0.0.0 --port 2401`

