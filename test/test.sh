#! /bin/bash
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
   if [[ "$APP_CONFIG" == "config/test_config.py" ]]
   then
        cd ..
        nosetests $1 --with-coverage --cover-package=rankomatic --cover-erase --cover-branches --cover-html
    else
        echo "Source me before running tests:"
        echo "   $ source test.sh && ./test.sh"
    fi
else
    echo "exporting test configuration"
    export APP_CONFIG=config/test_config.py
fi
