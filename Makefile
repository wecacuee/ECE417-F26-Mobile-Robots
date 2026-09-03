QUIZ_MDS := $(wildcard notebooks/*/quiz_*.md)
QUIZ_ZIPS := $(QUIZ_MDS:.md=.zip)

all: \
	build-html/01-19-intro-to-robotics.html \
	build-html/Python_3.html \
	build-html/ways-to-run-python.html \
	$(QUIZ_ZIPS)

.SECONDARY:


build-html/01-19-intro-to-robotics.html: chapters/00-intro/01-19-intro-to-robotics.md
	pandoc -f markdown -t html "$<" -o "$@"

build-html/%.html: chapters/01-py-intro/%.ipynb
	jupyter nbconvert --to html --embed-images \
		--theme jupyterlab-theme-githublight \
    	--config ./nbconvert_config.py \
        --output-dir "$(@D)" --output "$(basename $(@F))" "$<"


notebooks/045-layers-blocks-models/exports-%Colab.ipynb: notebooks/045-layers-blocks-models/%.ipynb
	python3 scripts/export_ipynb_to_colab.py $<

####################################################3

build-html/%.html: notebooks/045-layers-blocks-models/exports-%Colab.ipynb
	jupyter nbconvert --to html --embed-images \
		--theme jupyterlab-theme-githublight \
    	--config ./nbconvert_config.py \
        --output-dir "$(@D)" --output "$(basename $(@F))" "$<"

build-pdf/%.pdf: notebooks/045-layers-blocks-models/exports-%Colab.ipynb
	jupyter nbconvert --to webpdf --embed-images \
		--theme jupyterlab-theme-githublight \
    	--config ./nbconvert_config.py \
        --output-dir "$(@D)" --output "$(basename $(@F))" "$<"


%.zip: %.md
	pandoc -f markdown+latex_macros+tex_math_dollars -t html --mathml --no-highlight $< -o "$*.html"
	text2qti --template=brightspace $<
