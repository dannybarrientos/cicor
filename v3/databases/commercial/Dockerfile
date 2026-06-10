FROM postgres:15-alpine

LABEL module="cicor-commercial" \
      description="CICOR ERP - PostgreSQL DB: Módulo Comercial"

ENV POSTGRES_DB=commercial_db \
    POSTGRES_USER=commercial_user \
    POSTGRES_PASSWORD=commercial_pass \
    PGDATA=/var/lib/postgresql/data/pgdata

COPY init.sql /docker-entrypoint-initdb.d/init.sql
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 5432

ENTRYPOINT ["/entrypoint.sh"]
