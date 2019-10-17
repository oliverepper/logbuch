LOGBUCH_VERSION='0.1'

run-logbuch: instance/app.db
	flask run

instance/app.db: instance/secret_key
	flask db upgrade
	flask logbuch init-db

instance/secret_key:
	mkdir -p instance
	head -c 32 /dev/urandom > instance/secret_key

clean/all:
	rm -rf instance