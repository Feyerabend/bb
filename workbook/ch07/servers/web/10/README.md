
## Microservices

This example illustrates a microservices architecture through three interconnected services:
Inventory, Pricing, and Order. Each service operates independently, showcasing fundamental
microservices concepts such as loose coupling, independent deployment, and scalability. Below,
we explore the architecture, the functionality of each service, and the key microservices
patterns demonstrated, with an emphasis on the underlying principles of microservices.


### Understanding Microservices

Microservices are an architectural style where an application is structured as a collection
of small, autonomous services, each responsible for a specific business capability. Unlike
monolithic architectures, where all functionality resides in a single codebase, microservices
are independently deployable, communicate over well-defined interfaces (typically APIs),
and are organised around business domains.

- *Loose Coupling*: Services operate independently, reducing dependencies and allowing
  changes to one service without impacting others.
- *Independent Scalability*: Each service can be scaled based on its specific demand,
  optimising resource usage.
- *Resilience*: Failures in one service are isolated, preventing cascading failures
  across the system.
- *Decentralised Data Management*: Each service manages its own data, avoiding shared
  databases to maintain autonomy.
- *Technology Diversity*: Different services can use different technologies, enabling
  teams to choose the best tools for their tasks.
- *Continuous Delivery*: Microservices support frequent, independent deployments,
  enabling faster updates and innovation.

These principles are reflected in the example's design, where each service handles a distinct
function, communicates via HTTP APIs, and maintains its own data.


### Architecture Overview

The system comprises three services and a web client:

```
┌─────────────────┐     ┌─────────────────┐      ┌─────────────────┐
│  Inventory      │     │  Pricing        │      │  Order          │
│  Service        │     │  Service        │      │  Service        │
│  :7001          │     │  :7003          │      │  :7002          │
└─────────────────┘     └─────────────────┘      └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        ┌─────────────────┐
                        │    Web Client   │
                        │     Browser     │
                        └─────────────────┘
```

- *Inventory Service* (:7001): Manages product inventory, providing stock levels and item details.
- *Pricing Service* (:7003): Handles pricing logic, including discounts and bulk pricing queries.
- *Order Service* (:7002): Orchestrates order creation by aggregating data from Inventory and Pricing services.
- *Web Client*: A browser-based interface for interacting with the services, demonstrating real-world usage.

Each service is self-contained, with its own HTTP server, data store, and endpoints,
embodying the microservices principle of autonomy.


### Service 1: Inventory Service

The Inventory Service manages product data, including stock levels and categories. It supports
queries for individual items, filtered lists by category, and health checks. The service simulates
real-world scenarios like occasional delays to mimic network latency or processing overhead,
ensuring robustness in handling variable response times.

*File: `inventory_service.py`*

This service exemplifies microservices' single-responsibility principle, focusing solely on
inventory management. Its endpoints are designed for flexibility, supporting both broad queries
and specific item lookups, with health checks ensuring service reliability.


### Service 2: Pricing Service

The Pricing Service calculates prices for items, incorporating discounts and supporting bulk
pricing requests. It simulates occasional failures to demonstrate fault tolerance, a critical
aspect of microservices resilience. The service provides detailed pricing information, including
currency and discount status.

*File: `pricing_service.py`*

The Pricing Service demonstrates microservices' ability to handle specialised tasks, with
endpoints designed for both individual and bulk operations, enhancing efficiency for clients
needing multiple price points.


### Service 3: Order Service

The Order Service orchestrates order creation by integrating data from the Inventory and
Pricing services. It employs a circuit breaker pattern to manage dependencies, ensuring
resilience against downstream failures. The service validates inventory availability and
aggregates pricing, providing a comprehensive order summary.

*File: `order_service.py`*

This service highlights microservices' data composition, aggregating information from
multiple sources to fulfill a business function, while its circuit breaker implementation
enhances fault tolerance.


### Web Client

The web client provides an interactive interface for users to explore the services. It
includes buttons for common operations, displays responses with feedback, and runs a demo
sequence on page load to showcase typical interactions.

*File: `client.html`*

The client enhances user interaction by providing a visual interface, aligning with
microservices' focus on enabling flexible client interactions through standardised APIs.


### Running the System

#### Terminal Setup

To run the system, open four terminal windows and execute the following commands:

```bash
# Terminal 1 - Inventory Service
python3 inventory_service.py

# Terminal 2 - Pricing Service  
python3 pricing_service.py

# Terminal 3 - Order Service
python3 order_service.py

# Terminal 4 - Open client
open client.html  # or python3 -m http.server 8000
```

These commands start each service on its designated port and serve the web client,
either by opening it directly or hosting it via a simple HTTP server.


#### Quick Test Commands

To verify the services, use these `curl` commands:

```bash
# Test inventory
curl http://localhost:7001/items
curl http://localhost:7001/items/A001
curl http://localhost:7001/health

# Test pricing
curl http://localhost:7003/price/A001
curl http://localhost:7003/health

# Test order creation
curl -X POST http://localhost:7002/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "test", "skus": ["A001", "B001"]}'

# Health checks
curl http://localhost:7002/health
```

These commands test key functionalities, ensuring services respond correctly and
handle errors appropriately.


### Key Microservices Patterns Demonstrated

The example incorporates several microservices design patterns, each addressing
specific challenges in distributed systems:

1. *Service Discovery*: Services use hardcoded URLs for simplicity, but include health
   check endpoints to monitor availability, a foundation for dynamic discovery in
   production environments using tools like Consul or Eureka.
2. *Circuit Breaker Pattern*: The Order Service employs circuit breakers to prevent
   cascading failures, automatically recovering after a timeout and using fallback
   responses to maintain functionality during service outages.
3. *Graceful Degradation*: The system continues operating despite partial failures,
   such as the Order Service using fallback pricing when the Pricing Service is
   unavailable, ensuring user-facing functionality remains intact.
4. *Timeout Handling*: Network requests include configurable timeouts to prevent
   hanging, enhancing system responsiveness and reliability.
5. *Error Propagation*: Services return structured error responses with appropriate
   HTTP status codes, providing clear feedback for debugging and client handling.
6. *Data Composition*: The Order Service aggregates data from Inventory and Pricing
   services, creating enriched responses that fulfill complex business requirements.
7. *CORS Support*: Cross-origin resource sharing is implemented to support browser-based
   clients, ensuring accessibility across different domains.

These patterns enhance the system's resilience, scalability, and maintainability,
core goals of microservices architecture.


### Production Considerations

While this example provides a robust foundation for understanding microservices,
production systems require additional components:

- *Load Balancing*: Deploy multiple instances of each service to distribute traffic
  and improve availability, using tools like NGINX or cloud-based load balancers.
- *Authentication*: Implement JWT tokens or API keys to secure service interactions,
  ensuring only authorised clients access the APIs.
- *Rate Limiting*: Protect services from abuse by limiting request rates, preserving
  performance under high load.
- *Logging*: Use structured logging with correlation IDs to trace requests across
  services, aiding in debugging and monitoring.
- *Metrics*: Integrate Prometheus or similar tools for real-time monitoring and
  performance dashboards.
- *Configuration*: Manage service configurations via environment variables or configuration
  services for flexibility across environments.
- *Database*: Replace in-memory data stores with persistent databases like PostgreSQL
  or MongoDB for data durability.
- *Message Queues*: Introduce asynchronous communication with tools like RabbitMQ or
  Kafka for handling high-volume, non-blocking operations.
- *API Gateway*: Use a gateway like Kong or AWS API Gateway to provide a single entry
  point, manage routing, and enforce policies.
- *Container Orchestration*: Deploy services using Kubernetes or Docker Swarm for
  automated scaling, deployment, and management.

These enhancements address scalability, security, and operational needs, making the system
production-ready while maintaining the microservices principles of autonomy and loose coupling.


### Conclusion

This example demonstrates the power of microservices in creating modular, resilient, and
scalable systems. By breaking down functionality into independent services, the architecture
supports flexible development, deployment, and maintenance. The included patterns—service
discovery, circuit breakers, and graceful degradation—address common challenges in distributed
systems, while the web client illustrates practical usage. Extending this foundation with
production-grade features can transform it into a robust, enterprise-ready solution, fully
leveraging the benefits of microservices architecture.

