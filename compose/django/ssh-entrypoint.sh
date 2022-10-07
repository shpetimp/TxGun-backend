#!/bin/bash

# Copy ECS env vars into bash profile so they're available to SSH'd users
echo "export ENV=$ENV" >> /etc/profile
echo "export SERVICE=$SERVICE" >> /etc/profile

exec "$@"
