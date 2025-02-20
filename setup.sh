#!/bin/bash

CURRENT_ABS_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "Adding templify aliases to .bashrc"

cat << EOF >> ~/.bashrc

# templify
alias templify-help='python ${CURRENT_ABS_PATH}/template_updater.py -h'
alias templify-clean='rm -f ${CURRENT_ABS_PATH}/updated_template_set.sql'
alias templify-edit='templify-clean && nano ${CURRENT_ABS_PATH}/updated_template_set.sql'
alias templify='templify-edit && python ${CURRENT_ABS_PATH}/template_updater.py'

EOF

echo "Reloading .bashrc"
source ~/.bashrc

echo "Done, start templifying!"
echo "templify-help for help"
