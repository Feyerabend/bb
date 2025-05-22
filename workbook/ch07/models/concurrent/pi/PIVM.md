

1. Basic Example (P and Q)

sequenceDiagram
    participant P
    participant a as Channel a
    participant Q
    
    P->>a: send(42)
    a->>Q: receive(x)
    Q->>Q: log(x=42)



2. Advanced Example (Client-Server-Coordinator)

sequenceDiagram
    participant Coordinator
    participant Server
    participant Client
    participant reply_ch as Channel reply_ch
    participant request as Channel request
    participant reply as Channel reply
    
    Coordinator->>reply_ch: create
    Coordinator->>request: create
    Coordinator->>reply: create
    Coordinator->>Server: spawn
    Server->>reply_ch: send(reply)
    Coordinator->>Client: send(reply_ch)
    Client->>request: send(42)
    Server->>request: receive(client_msg)
    Server->>reply: send(client_msg+100)
    Client->>reply: receive(response)
    Client->>Client: log(response)


3. Replication Example (Request Handlers)


sequenceDiagram
    participant Client
    participant Handler
    participant h1 as Handler1
    participant h2 as Handler2
    participant h3 as Handler3
    participant requests as Channel requests
    participant response_ch as Channel response_ch
    
    Handler->>requests: create
    Handler->>response_ch: create
    Handler->>h1: spawn
    Handler->>h2: spawn
    Handler->>h3: spawn
    
    Client->>requests: send(1)
    Handler->>h1: forward(1)
    h1->>response_ch: send(2)
    
    Client->>requests: send(2)
    Handler->>h2: forward(2)
    h2->>response_ch: send(3)
    
    Client->>requests: send(3)
    Handler->>h3: forward(3)
    h3->>response_ch: send(4)
    
    Client->>response_ch: receive(resp1=2)
    Client->>response_ch: receive(resp2=3)
    Client->>response_ch: receive(resp3=4)


