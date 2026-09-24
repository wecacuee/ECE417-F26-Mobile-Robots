QUIZ_MDS := $(wildcard chapters/*/quiz_*.md)
QUIZ_ZIPS := $(QUIZ_MDS:.md=.zip)

all: \
	build-html/01-19-intro-to-robotics.html \
	build-html/Python_3.html \
	build-html/ways-to-run-python.html \
	build-html/DiscretePlanning.html \
	build-pdf/DiscretePlanning.pdf \
	build-html/PRM.html \
	build-pdf/PRM.pdf \
	build-html/RRT.html \
	build-pdf/RRT.pdf \
	chapters/01-1901-discrete-planning/exports-DiscretePlanningColab.ipynb \
	chapters/01-1901-discrete-planning/DiscretePlanning.ipynb \
	chapters/01-1901-discrete-planning/exports-RRT.ipynb \
	chapters/01-1901-discrete-planning/exports-PRM.ipynb \
	chapters/01-1901-discrete-planning/DiscretePlanning.ipynb \
	chapters/01-1901-discrete-planning/exports/DiscretePlanning.pptx \
	$(QUIZ_ZIPS)

.SECONDARY:


build-html/01-19-intro-to-robotics.html: chapters/00-intro/01-19-intro-to-robotics.md
	pandoc -f markdown -t html "$<" -o "$@"

build-html/%.html: chapters/01-1901-discrete-planning/%.ipynb
	jupyter nbconvert --to html --embed-images \
		--theme jupyterlab-theme-githublight \
    	--config ./nbconvert_config.py \
        --output-dir "$(@D)" --output "$(basename $(@F))" "$<"

build-html/%.html: chapters/01-py-intro/%.ipynb
	jupyter nbconvert --to html --embed-images \
		--theme jupyterlab-theme-githublight \
    	--config ./nbconvert_config.py \
        --output-dir "$(@D)" --output "$(basename $(@F))" "$<"

chapters/01-1901-discrete-planning/exports-%Colab.ipynb: chapters/01-1901-discrete-planning/%.ipynb
	python3 scripts/export_ipynb_to_colab.py $<

# Lecture-deck slides, built from the single-source-of-truth SLIDES list.
chapters/01-1901-discrete-planning/exports/DiscretePlanning.pptx: \
		chapters/01-1901-discrete-planning/deck/talk_content.py \
		scripts/build_deck.py
	mkdir -p "$(@D)"
	python3 scripts/build_deck.py chapters/01-1901-discrete-planning/deck/talk_content.py "$@"

chapters/01-1901-discrete-planning/deck/slides/index.html: \
		chapters/01-1901-discrete-planning/deck/talk_content.py \
		scripts/build_reveal.py
	python3 scripts/build_reveal.py chapters/01-1901-discrete-planning/deck/talk_content.py

chapters/045-layers-blocks-models/exports-%Colab.ipynb: chapters/045-layers-blocks-models/%.ipynb
	python3 scripts/export_ipynb_to_colab.py $<

####################################################3

build-pdf/%.pdf: chapters/01-1901-discrete-planning/exports-%Colab.ipynb
	jupyter nbconvert --to webpdf --embed-images \
		--theme jupyterlab-theme-githublight \
    	--config ./nbconvert_config.py \
        --output-dir "$(@D)" --output "$(basename $(@F))" "$<"

build-html/%.html: chapters/045-layers-blocks-models/exports-%Colab.ipynb
	jupyter nbconvert --to html --embed-images \
		--theme jupyterlab-theme-githublight \
    	--config ./nbconvert_config.py \
        --output-dir "$(@D)" --output "$(basename $(@F))" "$<"

build-pdf/%.pdf: chapters/045-layers-blocks-models/exports-%Colab.ipynb
	jupyter nbconvert --to webpdf --embed-images \
		--theme jupyterlab-theme-githublight \
    	--config ./nbconvert_config.py \
        --output-dir "$(@D)" --output "$(basename $(@F))" "$<"


%.zip: %.md
	pandoc -f markdown+latex_macros+tex_math_dollars -t html --mathml --no-highlight $< -o "$*.html"
	text2qti --template=brightspace $<
