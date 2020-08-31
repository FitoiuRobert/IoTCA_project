#!/usr/bin/env bash

old_name="async"
new_name="async_module"
firebase_dir=$(find . -type d -name "firebase")


for file in ${firebase_dir}/* ; do
    [[ ! -f ${file} ]] && continue
    if grep -q ".${old_name}" ${file}; then
        sed -i "s/.${old_name} /.${new_name} /g" ${file}
        continue
    fi
    if [[ "${file}" == *"${old_name}.py" ]]; then
        mv "${file}" "${file%/*}/${new_name}.py"
    fi
done