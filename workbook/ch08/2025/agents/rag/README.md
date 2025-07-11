
## RAG: Retrieval-Augmented Generation

This code creates a web application that searches the LIBRIS database (Sweden's national library catalog)
with an added AI-powered ranking system.

*Basic Search*: The app lets you search through Sweden's library catalog for books, articles, and other
materials. You can get results in JSON (but can easily be expanded to citation formats like Harvard and Oxford, or
structured data formats).

*Enhanced with AI*: What makes this special is the "RAG" (Retrieval-Augmented Generation) feature that
uses AI to improve search results.

### How RAG Works Here

*Traditional Search*: Normally, library searches work like basic keyword matching--if you search for
"climate change," or "artificial intelligence," you get results that contain those exact words.

*RAG Enhancement*: This app adds an AI layer that:
1. *Understands Meaning*: Uses a machine learning model to understand what
   your search query actually *means*, not just the words

2. *Ranks by Relevance*: Compares your query's meaning to each search result's
   meaning and gives similarity scores

3. *Reorders Results*: Shows the most semantically relevant results first,
   even if they don't contain your exact keywords


### The AI/ML Components

*Embedding Model*: Uses a pre-trained model called "all-MiniLM-L6-v2" that converts text
into numerical vectors (embeddings) that capture semantic meaning.

*Similarity Calculation*: Uses cosine similarity to measure how "close" your query is to
each search result in this numerical space.

*Example*: If you search for "global warming," traditional search might miss a relevant book
titled "Climate Crisis Solutions" because it doesn't contain those exact words. The RAG
system would recognise these topics are related and rank that book higher.


### Technical Flow

1. You enter a search query
2. App searches LIBRIS database
3. If RAG is enabled, it:
   - Converts your query into an embedding
   - Converts each result into an embedding
   - Calculates similarity scores
   - Reorders results by relevance
4. Displays results with similarity scores

This represents a practical application of modern AI to improve traditional information
retrieval systems, making library searches more intelligent and contextually aware.

* Semantic Understanding: Finds relevant results even when exact keywords don't match
* Relevance Ranking: Results are ordered by meaning, not just keyword frequency
* Real-time Processing: Runs entirely in the browser without server dependencies

The application essentially transforms basic keyword search into intelligent semantic search,
making it much more effective at finding relevant library resources.


#### Core Functions

__1. Model Loading (loadModel)__

- Downloads and initializes a machine learning model that understands text meaning
- Uses the "all-MiniLM-L6-v2" model for creating text embeddings
- Shows loading status to the user

__2. Semantic Analysis (getEmbedding, cosineSimilarity)__

- Converts text into numerical vectors (embeddings) that capture meaning
- Compares how similar two pieces of text are using cosine similarity
- This allows ranking results by relevance rather than just keyword matching

__3. API Integration (fetchLibrisResults)__

- Connects to the LIBRIS API (Swedish library database)
- Fetches bibliographic records in JSON format (limited, but can be expanded)
- Handles API errors and response parsing

__4. Search and Ranking (searchLibris)__

- Takes user's search query and fetches results from LIBRIS
- Creates embeddings for both the search query and each result
- Calculates similarity scores between query and results
- Sorts results by semantic relevance (most similar first)

__5. Display System (displayResults, pagination functions)__

- Shows results with their similarity scores
- Displays full JSON data for each record
- Handles pagination for large result sets
- Updates UI states (loading, errors, etc.)


### Connection to AI Agents

While this isn't a full AI agent, it demonstrates several foundational concepts that bridge
toward agentic systems:

#### 1. Semantic Understanding
- The system "understands" the meaning of queries beyond keywords
- It can match conceptually related content even without exact word matches
- This semantic layer is crucial for agents that need to interpret user intent

#### 2. Dynamic Decision Making
- The system chooses whether to apply RAG ranking based on model availability
- It adapts its behaviour based on the success/failure of different components
- These conditional behaviours are stepping stones toward more autonomous decision-making

#### 3. Multi-Modal Processing
- Processes and transforms data dynamically based on context
- This flexibility is essential for agents that need to work with diverse data sources


### Path to Full AI Agents

This RAG foundation could evolve into a more agentic system by adding several key capabilities.
Query understanding and planning would allow the system to analyse complex requests and develop
multi-step strategies. For instance, when a user asks to "find recent AI papers similar to
transformers," an agent could break this down into searching for transformer-related papers,
filtering by publication date, and then finding semantically similar work based on those initial
results.

Autonomous actions would enable the system to operate more independently by auto-refining searches
based on result quality, following citations to build comprehensive research maps, and combining
multiple data sources beyond just LIBRIS. This would transform the system from a passive search
tool into an active research assistant that can iteratively improve its results and explore related
information networks.

Conversational memory would add continuity by remembering previous searches within a session, building
on earlier queries to refine results, and learning user preferences over time. This would create a
more personalised experience where the system becomes increasingly attuned to individual research
patterns and interests.

Tool integration would extend the system's utility by automatically exporting results to reference
managers, generating summaries or research briefs, and connecting to other academic databases. This
would create a seamless workflow where the system not only finds relevant information but also helps
users organise and utilise it effectively, transforming from a search interface into a comprehensive
research companion.

### Why This Matters

The RAG approach here solves a key problem that traditional search engines face--the
*semantic gap* between how users express their needs and how information is indexed.
By adding semantic understanding, the system becomes more "intelligent" in matching
user intent with relevant content.

This is foundational for AI agents because agents need to:
- Understand user goals (not just commands)
- Find relevant information across large knowledge bases
- Make connections between related concepts
- Provide contextually appropriate responses

The LIBRIS application shows how RAG can transform a simple search interface into something
more intelligent and user-friendly.


