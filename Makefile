.PHONY: frontend frontend_dev

all: frontend messages

frontend:
	make -C frontend

dev:
	make -C frontend dev

frontend_dev:
	make -C frontend dev

messages:
	egrep -R "bsiconbox|table_ord_helper" templates | python parse_special_translations.py > mobishopper/special_translations.py
	./manage.py makemsmessages --domain djangojs -l pl --ignore frontend
	./manage.py makemsmessages --domain django -l pl --ignore frontend
	./manage.py compilemessages
