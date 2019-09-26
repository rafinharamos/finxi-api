# finxi-api
Api para o desafio finxi

## Executando o Servidor

1. Abra um terminal e navegue até a pasta root do projeto

2. Construindo o container:

```
docker-compose build
```

3. Migrando o banco de dados:
```
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate
```

4. Criando super usuário:

```
docker-compose run web python manage.py createsuperuser

```

5. Executando o container:

```
docker-compose up
```

6. Para rodar o postman com a collection, importe o arquivo finxi_bd.json na raiz do projeto que já tem os usuários e os tokens. Sem isso vai apresentar erro de acesso.
