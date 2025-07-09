
## RAG

This code creates a web application that searches the LIBRIS database (Sweden's national library catalog)
with an added AI-powered ranking system. Let me break down what it does in simple terms:


*Basic Search*: The app lets you search through Sweden's library catalog for books, articles, and other
materials. You can get results in different formats like JSON, citation formats (Harvard, Oxford), or
structured data formats.

*Enhanced with AI*: What makes this special is the "RAG" (Retrieval-Augmented Generation) feature that
uses AI to improve search results.

### How RAG Works Here

*Traditional Search*: Normally, library searches work like basic keyword matching--if you search for
"climate change," you get results that contain those exact words.

*RAG Enhancement*: This app adds an AI layer that:
1. *Understands Meaning*: Uses a machine learning model to understand what your search query actually *means*, not just the words
2. *Ranks by Relevance*: Compares your query's meaning to each search result's meaning and gives similarity scores
3. *Reorders Results*: Shows the most semantically relevant results first, even if they don't contain your exact keywords


### The AI/ML Components

*Embedding Model*: Uses a pre-trained model called "all-MiniLM-L6-v2" that converts text
into numerical vectors (embeddings) that capture semantic meaning.

*Similarity Calculation*: Uses cosine similarity to measure how "close" your query is to
each search result in this numerical space.

*Example*: If you search for "global warming," traditional search might miss a relevant book
titled "Climate Crisis Solutions" because it doesn't contain those exact words. The RAG
system would recognize these topics are related and rank that book higher.


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

