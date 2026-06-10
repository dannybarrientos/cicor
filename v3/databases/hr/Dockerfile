FROM postgres:15-alpine

LABEL module="cicor-hr" \
      description="CICOR ERP - PostgreSQL DB: Módulo Recursos Humanos"

ENV POSTGRES_DB=hr_db \
    POSTGRES_USER=hr_user \
    POSTGRES_PASSWORD=hr_pass \
    PGDATA=/var/lib/postgresql/data/pgdata

COPY init.sql /docker-entrypoint-initdb.d/init.sql
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 5432

ENTRYPOINT ["/entrypoint.sh"]
