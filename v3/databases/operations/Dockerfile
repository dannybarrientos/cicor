FROM postgres:15-alpine

LABEL module="cicor-operations" \
      description="CICOR ERP - PostgreSQL DB: Módulo Operaciones"

ENV POSTGRES_DB=operations_db \
    POSTGRES_USER=operations_user \
    POSTGRES_PASSWORD=operations_pass \
    PGDATA=/var/lib/postgresql/data/pgdata

COPY init.sql /docker-entrypoint-initdb.d/init.sql
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 5432

ENTRYPOINT ["/entrypoint.sh"]
