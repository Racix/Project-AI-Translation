FROM mongo:latest

EXPOSE 27017


COPY init-script.js /docker-entrypoint-initdb.d/

CMD ["mongod"]