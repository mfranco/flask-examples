#!/bin/sh
/usr/bin/initdb 
/usr/bin/pg_ctl start
sleep 2
/usr/bin/psql -c "CREATE ROLE ds WITH ENCRYPTED PASSWORD 'dsps'";
/usr/bin/psql -c "ALTER ROLE ds WITH ENCRYPTED PASSWORD 'dsps'";
/usr/bin/psql -c "ALTER ROLE ds SET client_encoding TO 'utf8';"
/usr/bin/psql -c "ALTER ROLE ds  WITH LOGIN;"
/usr/bin/psql -c "ALTER ROLE ds SET default_transaction_isolation TO 'read committed';"
/usr/bin/psql -c "ALTER ROLE ds SET timezone TO 'UTC';"
/usr/bin/psql -c "CREATE DATABASE ds;"
/usr/bin/psql -c "CREATE DATABASE ds_test;"
/usr/bin/psql -c "ALTER DATABASE ds OWNER TO ds;"
/usr/bin/psql -c "ALTER DATABASE ds_test OWNER TO ds;"
/usr/bin/psql -c "GRANT ALL PRIVILEGES ON DATABASE ds to ds;"
/usr/bin/psql -c "GRANT ALL PRIVILEGES ON DATABASE ds_test to ds;"
/usr/bin/psql -c "CREATE DATABASE ds2;"
/usr/bin/psql -c "CREATE DATABASE ds2_test;"
/usr/bin/psql -c "ALTER DATABASE ds2 OWNER TO ds;"
/usr/bin/psql -c "ALTER DATABASE ds2_test OWNER TO ds;"
/usr/bin/psql -c "GRANT ALL PRIVILEGES ON DATABASE ds2 to ds;"
/usr/bin/psql -c "GRANT ALL PRIVILEGES ON DATABASE ds2_test to ds;"
echo 'host all all  all   md5' |  tee -a /postgresql/data/pg_hba.conf
echo "listen_addresses = '*'" |  tee -a  /postgresql/data/postgresql.conf
