FROM daocloud.io/learningtech/uwsgi:3.5-onbuild

RUN mkdir -p /var/www/retoohs/socket && mkdir -p /var/www/retoohs/static

RUN python3 manage.py collectstatic --noinput

RUN python3 manage.py bower install

CMD ["uwsgi", "--socket", "/var/www/retoohs/socket/retoohs.sock", "--module", "retoohs.wsgi", "--processes", "2"]

VOLUME ["/var/www/retoohs/socket", "/var/www/retoohs/static", "/var/www/retoohs/bower_components", "/var/www/retoohs/media"]
