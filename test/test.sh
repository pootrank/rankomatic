#! /bin/bash
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
   if [[ "$APP_CONFIG" == "config/test_config.py" ]]
   then
        cd ..
        nosetests "$@" --with-coverage --cover-package=rankomatic --cover-erase --cover-branches --cover-html --cover-html-dir=test/stats/cover --with-cprofile --cprofile-stats-file=test/stats/profile.dat --cprofile-stats-erase
    else
        echo "Source me before running tests:"
        echo "   $ source test.sh && ./test.sh"
    fi
else
    echo "exporting test configuration"
    export APP_CONFIG=config/test_config.py
    cprofilev stats/profile.dat &
fi
