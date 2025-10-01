
## Raspberry Pi Pico W Mesh Network with Automatic Role Assignment

Here we introduce a foundation for a distributed node coordination system.
This is essentially a leader election system with service discovery,
with some fundamental building blocks for distributed systems ..

The first demo system [01](./01/) creates a self-organising network where:

1. One Pico W acts as an Access Point (AP) and coordinator.
2. Client Picos connect and automatically get assigned roles
   based on join order.
3. The first client becomes MASTER, others become WORKER1, WORKER2, etc.
4. Nodes maintain peer-to-peer communication while the AP
   tracks membership.
5. Each node knows about all other nodes and their roles.
   After discovery, all Picos can communicate directly (peer-to-peer)
   using the list of IPs.



### Projects: Practical Extension Ideas

From the above we can explore further into the mesh of nodes:

[02](./02/). Distributed Environmental Monitoring
```
# Each node collects sensor data (temp, humidity, light)
# MASTER aggregates data and makes decisions
# WORKERs report to MASTER and execute commands
# Example: Smart greenhouse with multiple sensor nodes
```

03. Load-Balanced Task Queue
```
# MASTER receives tasks via web interface
# Distributes work among available WORKERs
# WORKERs report completion status
# Handles node failures gracefully
```

04. Distributed LED Matrix Display
```
# Each Pico controls a section of a larger display
# MASTER coordinates animations across all sections
# Creates seamless large-scale visual effects
```

05. IoT Device Orchestration
```
# Control multiple devices (lights, motors, sensors)
# MASTER acts as central command
# WORKERs control local hardware
# Web interface for monitoring/control
```

.. or make up your own project!
