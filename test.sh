#!/bin/bash
ARGS=("$@")
seqdir=${ARGS[0]}
aligndir=${ARGS[1]}

echo "this is the workdir: $seqdir"
echo "this is the alignmentdir: $aligndir"
echo "these are the other dirs: ${ARGS[@]:2}"
find "${ARGS[@]:2}" -name "*.sh" -type f


