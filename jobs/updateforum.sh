#!/bin/bash
cd /Users/viet_tran/Workplace/viettn85/KQL/KqlForum/
nohup python3 src/watch/getForumUpdate.py > logs/updatef.log &
# https://stackoverflow.com/questions/29338066/run-python-script-at-os-x-startup