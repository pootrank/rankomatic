#! /bin/bash

# get virtualenv
cd $HOME/.virtualenvs/otorder/bin
source activate

cd $PROJECT_DIR
python -m rankomatic.bin.tasks
