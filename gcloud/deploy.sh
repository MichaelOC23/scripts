#!/bin/bash

clear

gcloud run deploy simpleappservice \
    --source . \
    --platform managed \
    --region us-west2 \
    # --allow-unauthenticated
