# get the stuff we need
source `which virtualenvwrapper.sh`
workon ot_orders

# set environment variables
export APP_CONFIG=config/dev-config.py

# hit the gas
python runserver.py
