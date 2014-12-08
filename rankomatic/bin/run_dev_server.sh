# get the stuff we need
source `which virtualenvwrapper.sh`
workon otorder

# set environment variables
export APP_CONFIG=config/dev-config.py

# hit the gas
#python -m rankomatic.otorderd &
python runserver.py
