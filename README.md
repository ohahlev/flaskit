# FLASKIT
### project code set up

- create virtual env

	`virtualenv --python python3.6 env`
	
- activate virtual env

	`source env/bin/activate`
	
- install dependency and use dev config for postgresql

	`make install && make dev_pg`
		
### environment variable set up

- replace script/dev.sh and script/prod.sh with real value

### database set up

- create database name flaskit

- drop all tables

	`make drop_db`
		
- create all tables

	`make init_db`
	
- insert initalized data

	`make init_data`



	