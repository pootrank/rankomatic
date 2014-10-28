#! /bin/bash
export APP_CONFIG=config/test_config.py
cd ..
nosetests $1 --with-coverage --cover-package=rankomatic --cover-erase --cover-branches --cover-html
