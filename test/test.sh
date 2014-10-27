#! /bin/bash
cd ..
nosetests $1 --with-coverage --cover-package=rankomatic --cover-erase --cover-branches --cover-html
