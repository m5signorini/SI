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

all: clear_db populate_db setorder_db init_db setprice_db gettops_db searchmovies_db inventorycustomertrigger_db orderstrigger_db
raw_db: clear_db populate_db


# GESTION DE DB
########################

clear_db:
	dropdb --if-exists $(PGDATABASE)
	createdb

populate_db:
	gunzip -c dump_v1.4.sql.gz | psql si1

show_dbs:
	echo '\l' | psql


# MODIFICACIONES DE DB
#########################

init_db:
	psql -f actualiza.sql

setprice_db:
	psql -f setPrice.sql
setorder_db:
	psql -f setOrderAmount.sql
gettops_db:
	psql -f getTopActor.sql
	psql -f getTopSales.sql
searchmovies_db:
	psql -f searchMovies.sql
inventorycustomertrigger_db:
	psql -f updInventoryAndCustomer.sql
orderstrigger_db:
	psql -f updOrders.sql
