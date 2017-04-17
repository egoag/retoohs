# retoohs

Another site like [ss-panel](https://github.com/orvice/ss-panel), based on Django + AdminLTE.  
Demo: [https://retoohs.herokuapp.com](https://retoohs.herokuapp.com).  
*This project is under development* 

# Requirements

 -  Python 3.5
 -  Django 1.9
 -  Web Server (Nginx or Apache)
 
# Tutorial

Clone or download an release, install the requirements (or via virtualenv): 

`pip3 install -r requirements`

Initial database:

`python3 manage.py migrate`

Follow the instructions to create your admin account:

`python3 manage.py createsuperuser`

Start server:

`python3 manage.py runserver`

Now you can visit `http://localhost:8000` and see the result.

# Settings

You can customize settings file `retoohs/settings_local.py`, or use environment variables.  
For detail reference `retoohs/settings_local_sample.py`.

# Docker

Available Docker image is at [daocloud](http://dashboard.daocloud.io/packages/20dc328d-a26b-43ea-83d2-c4d8ce02bba0),
 with uWSGI as application server and socket file volumed at `/var/www/retoohs/socket/retoohs.sock`, 
 collected static files volumed at `/var/www/retoohs/static`.  
The `docker-compose.yml` example:
```
version: '2'

services:
  mysql:
    image: mysql:5.7
    restart: always
    ports:
      - "3306:3306"
    environment:
      - MYSQL_DATABASE=DBNAME
      - MYSQL_USER=DBUSER
      - MYSQL_PASSWORD=DBPWD
      - MYSQL_ROOT_PASSWORD=DBROOTPWD
  django: 
    image: daocloud.io/youyaochi/retoohs:latest
    restart: always
    links:
      - mysql:mysql
    environment:
      - DEBUG='false'
      - DB_TYPE=mysql
      - DB_HOST=mysql
      - DB_NAME=DBNAME
      - DB_USER=DBUSER
      - DB_PASS=DBPWD
  nginx:
    image: nginx:latest
    restart: always
    volumes: 
      - /PATH/TO/YOUR/NGINX.CONF:/etc/nginx/nginx.conf
    volumes_from:
      - django
    ports:
      - "443:443"
      - "80:80"
```

For nginx.conf:
```
...
upstream django {
    server    unix:///var/www/retoohs/socket/retoohs.sock;
}
...
location /static {
    root    /var/www/retoohs/;

}
...
```
