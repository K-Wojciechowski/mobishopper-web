.PHONY: output dev copy prod prodbuild devbuild

output: prodbuild copy

prod: output

dev: devbuild copy

prodbuild:
	npm run build

devbuild:
	npm run build_dev

copy:
	cp -r dist/js/* ../static/vue/
	cp -r node_modules/@ttskch/select2-bootstrap4-theme/dist/select2-bootstrap4.min.css ../static/
	cp -r node_modules/bootstrap-icons/bootstrap-icons.svg ../static/
