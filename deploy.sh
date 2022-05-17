#!/bin/sh

github.py cpc -m stash
docker deploy nailbiter/heartbeat_system
