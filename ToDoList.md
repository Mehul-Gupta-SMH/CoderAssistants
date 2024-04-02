# Project Todo List

## Tech Stack used

- [x] Autogen
- [x] Models : 
  - **LLM**
    - GPT-3.5-turbo (OpenAI)
    - Claude-2.0 (Anthropic)
    - Gemma-2b-it (Google)
  - **Embedding**
    - mxbai-embed-large-v1 (Mixedbread AI)
  - **CrossEmbedding**
    - mxbai-rerank-base-v1 (Mixedbread AI)
  - **Safety**
    - Toxicity 
      - bias-detection-model (d4data)
    - Bias
      - bias-detection-model (d4data)

## Project : Coder Assistants

- ### Code Assistant agent templates
  - #### Python Dev Team
    - [x] **Co-ordinating Manager**
      - [x] Technical Manager: Identifies which agent is required for the successive tasks. 
    - [x] **Developer Team**
      - [x] Project Planner: Breaks down the initial problem into simpler chunks to be done by the code writer
      - [x] Code Writer: Writes codes
      - [x] QA developer: Write code tests to be done
    - [ ] **Support Tools**
      - [ ] Code Repo: Identifies already existing code repository that can be used for development.
      - [ ] Code Testing support: Runs and checks if the codes work as intended.
  
  - #### SQL Dev Team
    - [x] Co-ordinating Manager
      - [x] Technical Manager: Identifies which agent is required for the successive tasks.
    - [x] Developer Team
      - [x] Lead Analyst: Breaks down the complex issues in smaller queries that can be used by the Senior analyst and Junior Analyst.
      - [x] Senior Analyst: Write queries for complex tasks 
      - [x] Junior Analyst: Write queries for simpler tasks 
    - [ ] Support Tools
      - [ ] Database Admin: Helps the Analyst team to write queries by providing context about the tables and columns that can be used for building queries.
      - [ ] Query Testing support: Runs and checks if the queries work as intended. 

- ### Code Migration
  - #### SAS to PySpark (TBD)
  - #### SAS to SQL (TBD)
  - #### Python(Pandas) to PySpark (TBD) 


## Learning for future updates

- [ ] Using LiteLLM for supporting multiple API endpoints (https://docs.litellm.ai/)
- [ ] Check how Langfuse works (https://langfuse.com/)
  - [ ] For monitoring of the API use
- [ ] Control vectors and Representation Engineering
  - [ ] Control vectors (https://www.reddit.com/r/LocalLLaMA/comments/1atqj7f/control_vectors_add_a_meaningful_bias_in_each/)
  - [ ] Representation Engineering (https://vgel.me/posts/representation-engineering/)
- [ ] Running LLM locally
  - [ ] Ollama (https://github.com/ollama/ollama)
  - [ ] Llama.cpp (https://github.com/abetlen/llama-cpp-python)
- [ ] Simplify tool usage for agents
  - [ ] Semantic Router (https://github.com/aurelio-labs/semantic-router)
