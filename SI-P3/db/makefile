#
# 	Autores:
# 	Martin Sanchez Signorini
#
#

export PGDATABASE := si1
export PGUSER := alumnodb
export PGPASSWORD := alumnodb
export PGCLIENTENCODING := LATIN9
export PGHOST := localhost
PSQL = psql

# INICIALIZADORES
########################

all: clear_db populate_db
raw_db: clear_db populate_db


# GESTION DE DB
########################

clear_db:
	dropdb --if-exists $(PGDATABASE)
	createdb

populate_db:
	gunzip -c dump_v1.5-P3.sql.gz | psql si1

show_dbs:
	echo '\l' | psql


# MODIFICACIONES DE DB
#########################

trigger:
	psql -f updPromo.sql
