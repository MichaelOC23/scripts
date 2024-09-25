#!/bin/bash

clear

# docker build -t gcr.io/toolsexplorationfirebase/simpleapp .

# docker push gcr.io/toolsexplorationfirebase/simpleapp

gcloud run deploy simpleappservice \
    --source . \
    --platform managed \
    --region us-west2 \
    --allow-unauthenticated
