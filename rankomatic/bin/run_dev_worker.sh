source `which virtualenvwrapper.sh`
workon otorder

export APP_CONFIG=config/dev-config.py

python runworker.py
