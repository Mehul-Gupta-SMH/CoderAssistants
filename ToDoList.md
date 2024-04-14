# Project Todo List

## Tech Stack used

- [x] Autogen
- [x] Models : 
  - **LLM**
    - GPT-3.5-turbo (OpenAI)
    - claude-2.0 (Anthropic)
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

- ### Code Assistant agents templates
  - #### Python Dev Team
    - [x] **Co-ordinating Manager**
      - [x] Technical Manager : Identifies which agent is required for the successive tasks. 
    - [x] **Developer Team**
      - [x] Project Planner : Breaks down initial problem into simpler chunks to be done by code writer
      - [x] Code Writer : Writes codes
      - [x] QA developer : Write code tests to be done
    - [ ] **Support Tools**
      - [ ] Code Repo : Identifies already existing code repository that can be used for development.
      - [ ] Code Testing support : Runs and checks if the codes that works as intended.
  
  - #### SQL Dev Team
    - [x] Co-ordinating Manager
      - [x] Technical Manager : Identifies which agent is required for the successive tasks.
    - [x] Developer Team
      - [x] Lead Analyst : Breaks down the complex issues in smaller queries that can be used by the Senior analyst and Junior Analyst.
      - [x] Senior Analyst : Write queries for complex tasks 
      - [x] Junior Analyst : Write queries for simpler tasks 
    - [ ] Support Tools
      - [ ] Database Admin : Helps Analyst team to write queries by providing context about the tables and columns that can be used for building queries.
      - [ ] Query Testing support : Runs and checks if the queries that works as intended. 

- ### Code Migration
  - #### SAS to PySpark (TBD)
    - ##### Create a SQL Code and Assets repository (borrows Database Admin from SQL Dev team)
      - [ ] Tables and related metadata
        - [ ] Tables and their description
        - [ ] Tables Columns and their description
          [comment]: # (This resembles closely to a data dictionary.)
      - [ ] Relationships between tables
        - [ ] Join conditions from existing query repo
        - [ ] Keys mapping (FK,CK,PK etc)
      - [ ] Pre-existing queries as baseline 
        - [ ] Queries for specific request as example (especially if request is closely related or similar) 
    - ##### Create a PySpark Code repository (TBD) 
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
    - Could also be used for testing topics that needs to be guarded against.
      - Politics and/or Political Figures
      - Sensitive information (Creating explosives, biohazards etc.)
      - PII
      - HIPPA (Health, Insurance related)
    - Identify which agent / tool can be used for the next steps (building own agent framework?)