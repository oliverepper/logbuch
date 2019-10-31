all: ../app/static/generated ../app/templates/base_generated.html

../app/static/generated ../app/templates/base_generated.html: package-lock.json
	npm run build

package-lock.json:
	npm i

clean:
	rm -rf ../app/static/generated
	rm ../app/templates/base_generated.html