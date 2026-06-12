FROM postgres:15-alpine

LABEL module="cicor-inventory" \
      description="CICOR ERP - PostgreSQL DB: Módulo Inventario"

ENV POSTGRES_DB=inventory_db \
    POSTGRES_USER=inventory_user \
    POSTGRES_PASSWORD=inventory_pass \
    PGDATA=/var/lib/postgresql/data/pgdata

COPY init.sql /docker-entrypoint-initdb.d/init.sql
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 5432

ENTRYPOINT ["/entrypoint.sh"]
