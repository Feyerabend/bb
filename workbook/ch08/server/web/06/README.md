
## Web Client-Server Development

The story of web communication began in the 1990s with primitive but revolutionary technologies. I started
with the web around the winter 1994/1995. In those days, CGI (Common Gateway Interface) allowed servers to
execute Perl or Python scripts for each request, though this came at the cost of performance since every hit
spawned a new process. But also compiled C worked fine, as long as you had interface to the gateway. Alongside
this, SSI (Server Side Includes) provided basic dynamic content through simple directives embedded in HTML,
though its capabilities were extremely limited.

As we entered the 2000s, the landscape shifted dramatically with the rise of application servers. Technologies
like PHP, ASP, and JSP gained popularity by allowing developers to mix server-side code directly with HTML,
though this often led to tangled spaghetti code that was difficult to maintain. During this same period, more
structured approaches emerged with Java Servlets and .NET WebForms, which introduced object-oriented backend
logic but brought new complexities like the stateful ViewState in ASP.NET that could become unwieldy.

In the early 2000s, the web was obsessed with XML. XHTML emerged as a strict, XML-compliant version of HTML,
promising cleaner code. Paired with XSLT—a powerful language to transform XML into HTML—it aimed to separate
data (XML) from presentation (XSLT). Developers could serve pure data and let browsers render it via XSLT,
or pre-process it on the server. For a client I used this solution, generating HTML and images via ANT
(primarily build tool for Java).

The mid-2000s marked the Web 2.0 revolution, where AJAX and XMLHTTPRequest changed everything by enabling
JavaScript to fetch data in the background without full page reloads. This represented a fundamental shift
from server-rendered HTML to richer client-side logic. However, the dominant communication protocol of this
era, SOAP, proved problematic with its rigid XML-based RPC approach that was bloated and challenging to
debug, particularly for web applications.

By the 2010s, RESTful APIs had risen to dominance with their stateless, resource-based architecture that
organized everything around clean endpoints like 'GET /users/1'. This became the gold standard for web
services, perfectly complementing the new generation of Single-Page Applications (SPAs) built with
frameworks like React, Angular, and Vue that communicated with these REST backends.

The period from 2015 to the present has seen an explosion of modern alternatives addressing REST's limitations.
GraphQL emerged to solve over-fetching by letting clients request exactly what they needed, while gRPC
offered high-performance communication using binary Protocol Buffers over HTTP/2. Lightweight approaches
like JSON-RPC and WebSockets gained traction for specific use cases, and the serverless revolution began
with cloud functions and CDN-powered edge logic changing how we think about deployment.

Looking toward the future of the 2020s and beyond, WebAssembly promises near-native performance in browsers
for complex applications like Figma, while edge computing pushes logic physically closer to users to minimise
latency. This ongoing evolution continues to reshape how clients and servers communicate, with each generation
building on the lessons of the past while solving new challenges at web scale.


### CRUD vs. JSON-RPC

We offer some simple solutions in a technology that might have peaked.

| Feature        | *CRUD (REST-like)*                         | *JSON-RPC*                                |
|----------------|--------------------------------------------|-------------------------------------------|
| *Endpoint*     | Multiple (`/products`, `/cart`, `/orders`) | Single (`/api`)                           |
| *HTTP Methods* | GET, POST, PUT, DELETE                     | Only POST                                 |
| *Request Format* | Resource-based (`GET /products/123`)     | Command-based (`{"method":"get_product"}`)|
| *Flexibility*  | Limited to CRUD operations                 | Arbitrary commands (e.g., `apply_discount`) |
| *Complexity*   | Verbose (many endpoints)                   | Compact (single handler)                  |
| *Caching*      | Easy (HTTP caching)                        | Harder (custom logic)                     |
| *Best For*     | Simple, standardised APIs                  | Script-heavy systems                      |


### REST also ..

We have examplifed one technology here called CRUD. But often also REST is mentioned at the same time.
To be blunt: *REST is CRUD over HTTP with extra rules*. So how do they connect? *CRUD* is a *concept*
(Create, Read, Update, Delete), while *REST* is an *architectural style* that often uses CRUD operations
via HTTP methods.  


__CRUD (Basic Operations)__

A set of primitive operations for persistent storage:  
  - *C*reate (`INSERT` in SQL, `POST` in HTTP)  
  - *R*ead (`SELECT` in SQL, `GET` in HTTP)  
  - *U*pdate (`UPDATE` in SQL, `PUT/PATCH` in HTTP)  
  - *D*elete (`DELETE` in SQL, `DELETE` in HTTP)  

- Can be applied to databases, files, APIs, or any data storage.  
- Not tied to HTTP or the web.  

Example
  ```sql
  -- SQL (Database CRUD)
  INSERT INTO products (name, price) VALUES ('Keyboard', 50);
  ```

__REST (Web API Design)__

An architectural style for web services that *often* maps CRUD to HTTP methods:
  - `POST` → Create
  - `GET` → Read
  - `PUT/PATCH` → Update
  - `DELETE` → Delete

- Resource-based URLs (e.g., `/products/123`).
- Stateless: Each request contains all needed info.
- Uses HTTP standards (methods, status codes, headers).

Example
  ```http
  GET /api/products/123  # Read product 123
  DELETE /api/products/123  # Delete product 123
  ```

| Feature        | CRUD                    | REST                      |
|----------------|-------------------------|---------------------------|
| *Purpose*      | Data operations         | Web API design            |
| *Protocol*     | Any (SQL, files, etc.)  | HTTP only                 |
| *Methods*      | Generic (C/R/U/D)       | HTTP verbs (GET/POST/etc.)|
| *Structure*    | Not opinionated         | Resource URLs, stateless  |
| *Example*      | `db.insert(data)`       | `POST /api/data`          |

- REST can do more (e.g., `GET /search?q=term` isn't CRUD).
- CRUD can exist without REST (e.g., database CLI).

Advanced REST:
  - HATEOAS (hypermedia links in responses).
  - Caching, versioning, or bulk operations.
