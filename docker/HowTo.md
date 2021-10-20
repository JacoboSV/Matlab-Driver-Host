How to run server with docker
-----------------------------
1. Install docker and docker-compose
2. Go to the folder '{$Fusion Server}/docker/'
3. Run the following command:
```
docker-compose up
```
4 Initialize the server's database
```
docker-compose exec python manage.py loaddata fixtures/*.json
```