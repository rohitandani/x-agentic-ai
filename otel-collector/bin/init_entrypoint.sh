#!/bin/bash
if [ "$1" == "--generate-config" ]; then
  echo "Generating x-robot configuration..."
  mkdir -p /app/otel-collector/pipelines
  pip install PyYAML
  PYTHONPATH=/app/src python /app/otel-collector/bin/x-robot-gen.py \
    --defaults=/app/config/x_robot_ai_data.yaml \
    --receivers=/app/config/bigip_receivers.yml \
    --syslog=/app/config/syslog/syslog_data.yaml \
    --output=/app/otel-collector/x-robot-data.yaml \
    --receivers-output=/app/otel-collector/receivers.yml \
    --pipelines-output=/app/otel-collector/pipelines/pipelines.yml
  echo "Configuration generated in /app/otel-collector"
fi