
## LIBRIS Semantic Search with RAG

This web application searches Sweden's LIBRIS library catalog and enhances results with AI-powered
*Retrieval-Augmented Generation* (RAG) for semantic ranking.

### Features
- *Basic Search*: Search the LIBRIS catalog for books, articles, and more, with results returned in
  JSON format (expandable to other formats like Harvard or Oxford citations).
- *RAG Enhancement*: Uses AI to improve search result relevance by understanding query meaning,
  ranking results semantically, and prioritizing contextually relevant items.

### How RAG Works
- *Traditional Search*: Matches keywords (e.g., "climate change") to find exact or near matches in
  the catalog.
- *RAG System*:
  1. *Semantic Understanding*: Converts queries and results into numerical vectors (embeddings)
     using the `all-MiniLM-L6-v2` model to capture meaning.
  2. *Relevance Ranking*: Calculates cosine similarity between query and result embeddings to
     score relevance.
  3. *Result Reordering*: Prioritizes results based on semantic similarity, even if exact keywords
     are absent (e.g., a search for "global warming" may rank a book titled *Climate Crisis Solutions*
     highly).

### Technical Flow
1. User enters a search query.
2. App fetches results from the LIBRIS API.
3. If RAG is enabled:
   - Generates an embedding for the query.
   - Generates embeddings for each result (based on title, creator, description, etc.).
   - Computes similarity scores.
   - Ranks results by relevance.
4. Displays results with similarity scores and supports pagination.

### Search Strategies
- *Semantic Expansion*: Expands the query with related terms (e.g., "climate change" may include
  "global warming," "sustainability") and fetches a larger batch of results for semantic ranking.
- *Multi-Query*: Generates multiple related queries, fetches results for each, merges and deduplicates
  them, then ranks semantically.
- *Original + Ranking*: Uses the original query and applies semantic ranking to the results.

### Core Functions
1. *Model Loading (`loadModel`)*
   - Loads the `all-MiniLM-L6-v2` model for text embeddings.
   - Displays loading status in the UI.
2. *Semantic Analysis (`getEmbedding`, `cosineSimilarity`)*
   - Converts text to embeddings and calculates similarity scores for ranking.
3. *API Integration (`fetchLibrisResults`)*
   - Queries the LIBRIS API for bibliographic records in JSON.
   - Handles errors and response parsing.
4. *Search and Ranking (`searchLibris`)*
   - Processes the query based on the selected strategy.
   - Fetches, embeds, and ranks results by semantic relevance.
5. *Display System (`displayResults`, pagination)*
   - Shows ranked results with similarity scores.
   - Supports pagination and displays metadata (e.g., author, date, type).
   - Updates UI for loading, errors, and analytics.

### Analytics Display
- *Query Expansion*: Shows the original query and any added semantic terms.
- *Batch Info*: Displays the number of fetched results and ranking details.
- *Strategy Info*: Indicates the selected search strategy.
- *Merge Info*: Shows the number of results displayed per page.

### Connection to AI Agents
This application demonstrates foundational AI agent concepts:
- *Semantic Understanding*: Interprets query meaning beyond keywords, essential for understanding
  user intent.
- *Dynamic Decision Making*: Adapts based on model availability and strategy selection, a step toward
  autonomous systems.
- *Multi-Modal Processing*: Handles diverse data (text, API responses) dynamically, a key feature for
  versatile agents.

### Path to Full AI Agents
To evolve into a more agentic system, the app could:
- *Query Planning*: Break down complex queries into multi-step searches (e.g., for "recent AI papers
  similar to transformers," filter by date and find similar papers).
- *Autonomous Actions*: Auto-refine searches, follow citations, or integrate multiple data sources.
- *Conversational Memory*: Retain search history to refine results and learn user preferences.
- *Tool Integration*: Export results to reference managers, generate summaries, or connect to other
  databases.

### Why It Matters
The RAG system bridges the *semantic gap* in traditional search by aligning results with user intent,
not just keywords. This makes the app more intelligent and user-friendly, laying the groundwork for
advanced AI agents that can understand goals, retrieve relevant information, and provide contextually
appropriate responses.

