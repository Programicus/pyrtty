#!/bin/bash

#local script I have for convience functions
if [ -f ~/.local/scripts/.bashrc ]; then
    source ~/.local/scripts/.bashrc
fi

#findpi is defined above, but this block can be avoided by setting the appropriate env vars
if [[ -z $RASPBERRY_IP  ]] || [[ -z $RASPBERRY_UNAME ]] ; then
	findpi
fi

rsync -az --delete --exclude='.git/' --exclude='venv/' --exclude='sync-and-test.sh' . ${RASPBERRY_UNAME}@${RASPBERRY_IP}:~/pyrtty

VENV_USE_STR=""

function remote() {
	ssh ${RASPBERRY_UNAME}@${RASPBERRY_IP} "cd pyrtty;${VENV_USE_STR}${*}"
}

#Test if a remote environment has been setup
remote test -f "venv/bin/activate"
if [ "${?}" == "0" ]; then
	VENV_USE_STR="source venv/bin/activate;";
fi

remote python -u pyrtty.py