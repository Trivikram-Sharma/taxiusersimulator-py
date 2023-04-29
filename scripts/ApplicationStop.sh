#!/bin/bash
pid=pidof $(ps | grep 'python3 /TaxiUserSimulator/TaxiUserSimulator.py')
if [ $(pid) ]
    then
        if [ $(pid) ]
            then
                pkill pid
        else
             pkill 'python3 /TaxiUserSimulator/TaxiUserSimulator.py'
        fi
else
    echo 'No python ingestion process running'
fi
