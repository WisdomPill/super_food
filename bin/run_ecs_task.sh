#!/usr/bin/env bash
set -e
TIMEOUT=600
POLL_STEP=2
NUMBER='^[0-9]+$'

TASK_DEFINITION_ARN=$(aws ecs --region $1 describe-task-definition --task-def $3 | jq -r .taskDefinition.taskDefinitionArn)
RUN_TASK_RESULT=$(aws ecs --region $1 run-task --cluster $2 --task-definition $TASK_DEFINITION_ARN)
TASK_ARN=$(jq -r .tasks[0].taskArn <<< $RUN_TASK_RESULT)
if [ "$TASK_ARN" = "null" ]; then
    RUN_TASK_FAILURE=$(jq -r .failures[0] <<< $RUN_TASK_RESULT)
    echo "Could not start task:"
    echo $RUN_TASK_FAILURE
    exit 1
fi

i=0
while [ $i -lt $TIMEOUT ]; do
    DEF=$(aws ecs --region $1 describe-tasks --cluster $2 --tasks $TASK_ARN)
    STATUS=$(echo $DEF | jq -r .tasks[0].containers[0].lastStatus)
    echo "Task is $STATUS"
    if [ "$STATUS" != "PENDING" ] && [ "$STATUS" != "RUNNING" ]; then
        EXIT_CODE=$(echo $DEF | jq -r .tasks[0].containers[0].exitCode)
        if ! [[ $EXIT_CODE =~ $NUMBER ]]; then
            echo "Invalid exit code: $EXIT_CODE"
            exit 1
        fi
        echo "Task exited with code $EXIT_CODE"
        exit $EXIT_CODE
    else
        sleep $POLL_STEP
        i=$(( $i + $POLL_STEP ))
    fi
done

echo "Task timeout: ran more than $TIMEOUT seconds"
exit 1
