# get the stuff we need
source `which virtualenvwrapper.sh`
workon ot_orders

# set environment variables
export APP_CONFIG=config/dev-config.py

# cancel, kill, reschedule and restart background jobs
python schedule_jobs.py --cancel
kill $(ps -ax | grep [r]qscheduler | awk '{print $2}')
python schedule_jobs.py
rqscheduler &

# hit the gas
python runserver.py
