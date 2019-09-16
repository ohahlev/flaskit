install:
	pip install -r requirements.txt

dev_sqlite:
	cd app && ln -sf config_dev.py config.py

dev_pg:
	cd app && ln -sf config_dev_pg.py config.py

dev_mysql:
	cd app && ln -sf config_dev_mysql.py config.py

prod_sqlite:
	cd app && ln -sf config_prod.py config.py

prod_mysql:
	cd app && ln -sf config_prod_mysql.py config.py

prod_pg:
	cd app && ln -sf config_prod_pg.py config.py

drop_db:
	python manage.py drop_db

init_db:
	python manage.py init_db

init_data:
	python manage.py init_data

clean:
	pyclean .