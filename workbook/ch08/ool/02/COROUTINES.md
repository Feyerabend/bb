
## Object-Oriented Programming with Coroutines

Coroutines integrate well with OOP, allowing for:


### 1. Stateful Objects with Pausable Behavior

```python
class IterableSeries:
    def __init__(self, start, step):
        self.current = start
        self.step = step
    
    def __iter__(self):
        return self
    
    def __next__(self):
        value = self.current
        self.current += self.step
        return value

# using a generator-based approach
class GeneratorSeries:
    def __init__(self, start, step, max_items=None):
        self.start = start
        self.step = step
        self.max_items = max_items
    
    def generate(self):
        current = self.start
        count = 0
        while self.max_items is None or count < self.max_items:
            yield current
            current += self.step
            count += 1


series = GeneratorSeries(1, 2, 5)
for num in series.generate():
    print(num)  # Output: 1, 3, 5, 7, 9
```


### 2. Producer-Consumer Pattern

```python
class DataProducer:
    def __init__(self, data_source):
        self.data_source = data_source
    
    def produce(self):
        for item in self.data_source:
            # process item before yielding
            processed_item = self.process(item)
            yield processed_item
    
    def process(self, item):
        return item * 2

class DataConsumer:
    def consume(self, producer):
        for item in producer.produce():
            self.handle(item)
    
    def handle(self, item):
        print(f"Consumed: {item}")

producer = DataProducer([1, 2, 3, 4, 5])
consumer = DataConsumer()
consumer.consume(producer)  # Output: Consumed: 2, Consumed: 4, etc.
```


### 3. State Machines

```python
class StateMachine:
    def __init__(self, initial_state):
        self.state = initial_state
        self.handlers = {}
    
    def add_handler(self, state, handler):
        self.handlers[state] = handler
    
    def run(self):
        while self.state in self.handlers:
            # each handler is a generator coroutine
            handler = self.handlers[self.state]
            for next_state in handler():
                yield (self.state, next_state)
                self.state = next_state
                break
        yield (self.state, None)

def water_state_handler():
    print("Water is liquid")
    yield "ICE"

def ice_state_handler():
    print("Water is frozen")
    yield "STEAM"

def steam_state_handler():
    print("Water is vapor")
    yield "WATER"

machine = StateMachine("WATER")
machine.add_handler("WATER", water_state_handler)
machine.add_handler("ICE", ice_state_handler)
machine.add_handler("STEAM", steam_state_handler)

for transition in machine.run():
    print(f"Transitioned from {transition[0]} to {transition[1]}")
```


## Key Benefits of Coroutines in OOP

1. Encapsulation of State: Coroutines maintain their state between invocations, perfectly matching OOP's principle of encapsulation
2. Simplified Complex Flows: Sequential code for non-sequential processes
3. Efficient Resource Usage: No need for thread overhead when managing multiple operations
4. Clean Producer/Consumer Patterns: Clear separation of concerns between data producers and consumers
5. Testability: Easier to test incremental behavior

