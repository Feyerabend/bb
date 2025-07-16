
## Web Servers

These folders aim to provide a more comprehensible view of web servers, beginning with their relatively
simple architecture in the early 1990s. The first two parts ([01](./01/) and [02](./02/)) give some
background of the origin and connections to its history. Back then, servers were often monolithic
programs--sometimes even hand-written in C--that handled multiple client connections through basic
mechanisms like process forking or simple threading. Besides static pages, more dynamic content was
reached through CGI (Common Gateway Interface), and written in such languages as C or Perl. While
limited in scalability and features by today's standards, they were largely transparent in how they
worked. You could often read and understand the full codebase, or at least grasp the flow from
incoming request to outgoing response.

In contrast, modern cloud-based server environments—built on layers of containerisation, orchestration
(like Kubernetes), service meshes, and distributed storage--offer tremendous power and scalability, but
often at the cost of conceptual clarity. The complexity and abstraction make them harder to reason about,
especially from a educational code-level perspective. These earlier systems, though less capable, are
valuable pedagogically because they expose the core ideas of request handling, concurrency, and communication
in a direct and readable way.

Here in [03](./03/) very simple server, [04](./04/) threaded server, and [05](./05/) a threaded service, we
explore some simple servers, but also the evolving nature of web communication over the decades.
The early focus was firmly on the client-server model: a browser (the client) sent a request, and the server
responded with HTML. Each interaction was isolated—stateless and short-lived—often mediated through
protocols like HTTP/1.0, which assumed a new connection for each request.

Over time, this model began to shift. First came persistent connections and HTTP/1.1, which allowed multiple
requests over a single connection, improving efficiency. Then, AJAX (Asynchronous JavaScript and XML)
emerged in the mid-2000s, enabling web pages to update data dynamically without a full page reload. This
marked a subtle but important turn: the client began to take on more responsibility, and communication
became more interactive. As we can see from [06](./06/) AJAX improved on the otherwise stateless communication.

Later developments (like [07](./07/) and [08](./08/)) WebSockets, Server-Sent Events, and
HTTP/2 introduced full-duplex communication, multiplexing, and event-driven interactions. These changes
laid the groundwork for highly dynamic applications and real-time services, such as collaborative editing,
instant messaging, and live dashboards.

Meanwhile, the rise of RESTful APIs and microservices decoupled the client and server even further.
Frontend and backend teams could now develop independently, using JSON over HTTP as a universal interchange
format (cf. [09](./09/)). Eventually, this culminated in architectures like Single Page Applications
(SPAs) and serverless functions, where traditional notions of a "server" are abstracted away behind
layers of infrastructure.

Microservices [10](./10/) are an architectural style where applications are built as small, independent
services that handle specific functions and communicate via APIs. Unlike monoliths, they allow modular
development, independent deployment, and scaling, with each service managing its own data and logic.
This enables flexibility and faster development but adds complexity in managing distributed systems
and communication.

We now have a dedicated folder exploring the future of the web ([11](./11/)). What happens when AI and
machine learning take center stage? Could they reshape the web's core structure, replacing HTML with
Markdown or an entirely new format? Or might we transition to something radically different, like directly
executable content optimised for large language models (LLMs)? The web could evolve from a framework
of markup and rendering into a dynamic medium driven by real-time inference, semantics, personalisation,
and interaction--serving not only users but also machines.

What was once a simple model--browser asks, server answers--has evolved into a complex and often asynchronous
ecosystem. Understanding the older, simpler mechanisms is not just nostalgic; it's a way to build intuition
about what problems these new abstractions are solving, and at what cost in terms of visibility and control.


### Brief on Developments

In the early days, web servers were conceptually straightforward: you could write a basic server in C or
early scripting languages like Perl. For instance, a simple Python HTTP server using the built-in
"http.server" module closely resembles how early HTTP daemons (like NCSA HTTPd) handled requests:

```python
# Python 3.x
from http.server import HTTPServer, SimpleHTTPRequestHandler

server_address = ('', 8080)
httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
httpd.serve_forever()
```

This snippet encapsulates the core of the client-server model: listen on a socket, accept requests,
and return content.

But communication models changed. By the early 2000s, AJAX transformed how pages interacted with
servers, allowing background data exchange. Instead of refreshing the page, a JavaScript call might
request JSON data:

```javascript
fetch('/data')
  .then(response => response.json())
  .then(data => updatePage(data));
```

This pushed more logic to the client side, while the server shifted toward acting as a data provider.
That shift is even more pronounced in today's architectures. In a serverless deployment (e.g., AWS Lambda),
your entire server might be just a function:

```python
# AWS Lambda handler example
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from the cloud!'
    }
```

Here, the notion of a "server" vanishes--there's no process you control, no persistent socket, no filesystem.
The cloud provider handles routing, scaling, and lifecycle management.

In contrast to the clarity of that earlier Python HTTP server, this function executes in a managed, opaque
runtime. You gain scalability and integration, but you lose visibility. Debugging, performance tuning, and
even simple logging require navigating platform-specific layers.

These examples illustrate the ongoing trade-off in web architecture: from simplicity and transparency toward
abstraction and scalability. Each step reflects a shift in priorities--from developer control to deployment
efficiency, from code readability to operational complexity.
