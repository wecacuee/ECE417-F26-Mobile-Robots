export JUPYTER_PATH=$(realpath -m $(dirname ${BASH_SOURCE[0]}))/:$JUPYTER_PATH
jupyter --path
