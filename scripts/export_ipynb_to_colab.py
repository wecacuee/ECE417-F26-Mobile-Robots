import os
import os.path as osp
import nbformat
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def yaml_load(config_yaml="myst.yml"):
    with open(config_yaml) as cyf:
        data = load(cyf, Loader=Loader)
    return dict(repo_name=data['project']['github'])

OPEN_IN_COLAB_STRING="""
<div><a 
    target='_blank'
    href='https://colab.research.google.com/github/{repo_name}/blob/master/{file_path}'
    >
<span>OPEN IN COLAB</span></a></div>
"""

def main(notebookpath, mathaliasesnotebook, exportpath, config_yaml):
    variables = yaml_load(config_yaml)
    variables.update(dict(file_path=colab_filepath_create(notebookpath)))
    with (open(notebookpath) as nbfp,
          open(mathaliasesnotebook) as mafp):
        nb = nbformat.read(nbfp, 4)
        ma = nbformat.read(mafp, 4)
    #print(nb['cells'][0])
    nb['cells'][0] = ma['cells'][0]
    nb['cells'].insert(
            1,
            nbformat.v4.new_markdown_cell(
                source=OPEN_IN_COLAB_STRING.format(**variables)))
    print(f"Writing to '{exportpath}'")
    with open(exportpath, 'w') as exfp:
        nbformat.write(nb, exfp)

def ensuredirs(path):
    os.makedirs(osp.dirname(path), exist_ok=True)
    return path

def colab_filepath_create(nfilepath):
    root, ext = osp.splitext(osp.basename(nbfilepath))
    return osp.join(osp.dirname(sys.argv[1]), f"exports-{root}Colab{ext}")

if __name__ == '__main__':
    import sys
    nbfilepath = sys.argv[1]
    colab_filepath = colab_filepath_create(nbfilepath)
    mathaliasesnotebook = osp.join(
            osp.dirname(__file__ or "."),
            "../templates/math-aliases.ipynb")
    config_yaml  = osp.join(
            osp.dirname(__file__ or "."),
            "../myst.yml")
    main(sys.argv[1], 
         mathaliasesnotebook,
         ensuredirs(colab_filepath),
         config_yaml)

