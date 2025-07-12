
## Example: Semantics, back then ..

If we recapitulate the early evolution: The World Wide Web began in 1989–1990 as a human-readable hypertext
system, designed by Tim Berners-Lee at CERN to facilitate access to linked documents across a decentralised
network. It used HTML as a simple markup language, allowing authors to structure content into headers, paragraphs,
and hyperlinks. In these early years, the web was purely document-centric, and all of the *semantics*--meaning,
categorisation, intent--were implicit. Search engines like AltaVista and later Google had to infer relevance
using heuristics, frequency analysis, and primitive indexing methods.

By the late 1990s and early 2000s, Berners-Lee and others envisioned a richer version of the web, one where
content was not only human-readable but machine-understandable. This was the beginning of the *Semantic Web*
movement, formalised in a 2001 article in *Scientific American*. The idea was to annotate web content with
structured data and relationships, allowing intelligent agents to navigate, reason, and automate actions on
behalf of users. The foundational technologies were RDF (the Resource Description Framework), which expressed
statements as subject–predicate–object triples; OWL (the Web Ontology Language), which added formal logical
structure and reasoning capabilities; and SPARQL, a query language for extracting data from RDF graphs.

However, despite its theoretical power, the Semantic Web largely failed to gain widespread adoption. The reasons
were practical and sociotechnical. It was too difficult for average developers to use. It required careful
ontology design and maintenance. It offered little short-term reward compared to easier, more ad hoc techniques.
In many ways, it was a classic example of overengineering and underincentivization in web architecture.

A more pragmatic phase followed in the 2010s. Semantic markup shifted toward lightweight formats like JSON-LD,
schema.org tags, microdata, and OpenGraph metadata. These technologies were more accessible, required less
formalism, and directly served commercial purposes--especially in SEO, knowledge panels, social media previews,
and voice assistants. Rather than encoding full ontologies, developers annotated key pieces of content with
simplified schemas: product descriptions, event dates, article metadata. While this version of the semantic
web lacked the original vision’s logical rigor, it succeeded in embedding just enough structure into the
web to support machine interaction at scale.

Meanwhile, an even more significant shift began. The rise of large-scale machine learning, and especially deep
learning and language models, allowed systems to infer meaning from unstructured or semi-structured text
without relying on formal annotations. The emergence of transformer models like BERT, GPT, and others
around 2018–2020 introduced a new mode of semantics--not explicit or symbolic, but latent and distributed
across high-dimensional vector spaces. In this paradigm, instead of querying a structured graph of facts,
one uses natural language to probe vast learned representations. Search, summarisation, translation, and
question answering are all performed statistically, with impressive flexibility but often opaque reasoning.


### .. and now

This brings us to the present and near future. Language models such as GPT-4 and its successors have made
the web simultaneously more powerful and more fragile. On one hand, they enable new forms of interaction,
such as conversational browsing and dynamic content synthesis. On the other, they threaten to blur the
boundaries between human and machine-generated content, introduce contamination into training data, and
raise deep concerns about trust and provenance. As such, we may see a revival--not of the original semantic
web per se, but of its deeper goals: verifiability, transparency, and machine-readability of meaning.

Looking ahead, several developments seem likely. First, *vector-based representations* will become a new
substrate of the web. Web pages may be stored not just as HTML, but as embeddings--precomputed vector
encodings suitable for semantic search and retrieval. Instead of navigating via URLs or hyperlinks alone,
users (or agents) may traverse the web through semantic similarity. This will be less about navigating
location and more about exploring meaning-space. I guess there have to be to be standards that guide the
retrieval of data here.

Second, content may be written with language models in mind. Prompt-aware documents could include embedded
directives, summaries, or semantic hints for LLMs to consume, adapt, and complete dynamically. These
documents will not simply be static HTML pages but composable, queryable, and modifiable units that
adapt to context.

Third, provenance and trust will become central. The flood of synthetic content may push for cryptographic
watermarking, digital signatures, and provenance metadata--allowing users and models alike to distinguish
between human-authored, verified content and automatically generated noise. Technologies such as C2PA,
developed by Adobe and others, are early signals of this movement.

Lastly, the browser itself may change. Traditional interaction with the web--point-and-click,
read-and-scroll--may give way to agent-mediated interaction, where users state goals, and local or
cloud-based agents synthesize the necessary documents, tools, or summaries. Web pages may include
both display content and embedded interpretable structures--somewhere between executable
notebooks and semantic hypermedia.

In all of this, one can see the ghost of the semantic web still hovering. Not as an XML-based, logic-heavy
architecture, but as a set of aspirations: to make meaning computable, to make content composable,
and to build a web that is both dynamic and accountable.

| Era | Dominant Tech | Semantics Approach | Example Use |
|---|---|---|---|
| 1990s | HTML, HTTP | None / heuristic parsing | Static documents, hyperlinks |
| Early 2000s | RDF, OWL, SPARQL | Formal ontologies | Semantic web agents (prototype) |
| 2010s | JSON-LD, schema.org | Lightweight semantics | SEO, rich previews |
| 2020s | LLMs, embeddings, APIs | Statistical / latent | Chatbots, search, summarisation |
| 2030s? | LLM-agents, vectors, signed data | Prompt-aware, vector-native, provenance-verified | Dynamic synthesis, agent-webs |

