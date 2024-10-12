http://localhost:11434
  

# Remember to set all references to host.docker.internal:host-gateway.. READ ONLINE DOCKS easy fix for confusing

  
  docker run  \
  --add-host=host.docker.internal:host-gateway \
  --env=OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --env=USE_EMBEDDING_MODEL_DOCKER=sentence-transformers/all-MiniLM-L6-v2  \
  --env=USE_RERANKING_MODEL_DOCKER=  \
  --env=OPENAI_API_BASE_URL=  \
  --env=OPENAI_API_KEY="${OPENAI_API_KEY}" \
  --env=WEBUI_SECRET_KEY=  \
  --env=SCARF_NO_ANALYTICS=true  \
  --env=DO_NOT_TRACK=true  \
  --env=ANONYMIZED_TELEMETRY=false  \
  --env=WHISPER_MODEL=base  \
  --env=WHISPER_MODEL_DIR=/app/backend/data/cache/whisper/models  \
  --env=RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  \
  --env=RAG_RERANKING_MODEL=  \
  --env=SENTENCE_TRANSFORMERS_HOME=/app/backend/data/cache/embedding/models  \
  --env=HF_HOME=/app/backend/data/cache/embedding/models  \
  --env=DOCKER=true  \
  --volume=/Users/michasmi/data-llm/open-webui-data:/app/backend/data  \
  --workdir=/app/backend -p 3000:8080  \
  --restart=always  \
  --name open-webui ghcr.io/open-webui/open-webui:main 
  
sudo docker run -d -p 4000:8080 
--add-host=host.docker.internal:host-gateway 
-v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main and then I used host.docker.internal:11434 in the connection setting and now the Open Web UI can talk to Ollama :D – 
user13252132
 CommentedJun 3 at 12:06 
  
  docker run -d 
  --network=host 
  -v open-webui:/app/backend/data -e OLLAMA_BASE_URL=http://127.0.0.1:11434 --name open-webui --restart always ghcr.io/open-webui/open-webui:main



  
  
  
  
  
  
  
  docker run -d 
  --network=host 
  -v open-webui:/app/backend/data 
  -e OLLAMA_BASE_URL=http://127.0.0.1:11434 
  --name open-webui 
  --restart always ghcr.io/open-webui/open-webui:main



docker run -d 
-p 3000:8080 
--add-host=host.docker.internal:host-gateway 
-v open-webui:/app/backend/data -
-name open-webui 
--restart always ghcr.io/open-webui/open-webui:main
