FROM postgres:15-alpine

LABEL module="cicor-accounting" \
      description="CICOR ERP - PostgreSQL DB: Módulo Contabilidad"

ENV POSTGRES_DB=accounting_db \
    POSTGRES_USER=accounting_user \
    POSTGRES_PASSWORD=accounting_pass \
    PGDATA=/var/lib/postgresql/data/pgdata

COPY init.sql /docker-entrypoint-initdb.d/init.sql
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 5432

ENTRYPOINT ["/entrypoint.sh"]
