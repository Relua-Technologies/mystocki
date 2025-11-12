WEB_CONTAINER=web-project

up:
	docker compose up

down:
	docker compose down

debug:
	docker compose -f docker-compose-debug.yml up

logs:
	make exec cmd="tail -f /var/log/* 2>/dev/null || true"

bash:
	make exec cmd="bash"

env:
	test -f .env || cp .env-sample .env

setup:
	make env
	docker network create mystocki-network || true
	docker compose build --no-cache
	docker compose up -d
	make migrate
	make logs

restart:
	docker compose down && docker compose up -d

exec:
	docker compose exec $(WEB_CONTAINER) bash -c "$(cmd)"

migrations:
	make exec cmd="python manage.py makemigrations"

migrate:
	make exec cmd="python manage.py migrate"

rollback:
	make exec cmd="python manage.py migrate app $(rev)"

showmigrations:
	make exec cmd="python manage.py showmigrations"

shell:
	make exec cmd="python manage.py shell_plus || python manage.py shell"

createsuperuser:
	make exec cmd="python manage.py createsuperuser"

collectstatic:
	make exec cmd="python manage.py collectstatic --noinput"

runserver:
	make exec cmd="python manage.py runserver 0.0.0.0:8000"

compile:
	make exec cmd="npx tailwindcss -i ./static/input.css -o ./static/output.css --watch"

build-css:
	make exec cmd="npx tailwindcss -i ./static/input.css -o ./static/output.css"

test:
	make exec cmd="python manage.py test"

