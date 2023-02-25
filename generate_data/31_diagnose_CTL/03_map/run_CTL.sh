#!/bin/bash

tasks=0
max_tasks=2
#for model in SOM MLM EMOM POP2 ; do
for model in POP2 ; do
    
    tasks=$(( tasks + 1 ))

    casename="CTL_${model}"
  
    echo "$tasks"

    julia ../CESM-diagnostic/src/diagnose_scripts_julia/diagnose_model_opt.jl --diag-file diagnose_setting_CTL.toml --diagcase $model --diag-opt diag_opts.toml &
    
    if (( tasks == max_tasks )); then
        echo "Notice: max_tasks reached. Wait now."
        tasks=0
        wait
    fi

done
