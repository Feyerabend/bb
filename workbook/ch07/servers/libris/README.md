
## Simple Recommendation System

This code implements a simple content-based recommendation system for the
LIBRIS Xsearch interface. LIBRIS is a Swedish database for library items.
Searches can be performed through the API, which is described at:
* https://libris.kb.se/help/xsearch_eng.jsp?redirected=true&language=en

It's a very basic, but legitimate recommendation system.

1. *Knowledge Base Collection*: The system stores the last 50 search results
   in a "knowledgeBase" array, extracting key information (title, type, authors)
   and generating keywords.

2. *Keyword Extraction*: The `extractKeywords` function pulls keywords from
   titles and subjects, filtering out common words and short terms (less than 4
   characters).

3. *Recommendation Algorithm*: The `getRecommendations` function uses
   content-based filtering to:
   - Filter out the current item itself
   - Calculate a "score" based on the number of matching keywords
   - Filter items with scores > 0
   - Sort by score (highest first)
   - Return the top 3 items

4. *Limitations*:
   - It's extremely simple compared to production recommendation systems
   - The keyword extraction is rudimentary (basic word splitting)
   - There's no user personalisation (all recommendations are content-based)
   - The system is temporary (data exists only in the current session)
   - Limited to just 3 recommendations based on the first search result

This qualifies as a true recommendation system, albeit a very basic one. It attempts
to identify related items based on content similarity rather than just showing random
or popular items. However, it lacks sophistication compared to commercial recommendation
engines that use more complex algorithms, user behaviour data, and collaborative filtering.

For a small library search interface, this implementation provides simple "you might
also like" functionality without requiring complex infrastructure or backend processing.
