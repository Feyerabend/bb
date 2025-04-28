
## Flavours of State Machines

### 1. Deterministic Finite Automaton (DFA)

A DFA has one clear transition per input in each state. The traffic light
cycles normally or switches to Red for emergencies.

- States: Red, Green, Yellow
- Inputs: Timer (T), Emergency (E)
- Transitions:
  - Red + Timer → Green
  - Red + Emergency → Red (stay, already safe)
  - Green + Timer → Yellow
  - Green + Emergency → Red
  - Yellow + Timer → Red
  - Yellow + Emergency → Red
- Start State: Red
- Accept State: None (control system)

```python
class TrafficLightDFA:
    def __init__(self):
        self.state = "Red"
    
    def transition(self, input):
        if self.state == "Red":
            if input == "Timer":
                self.state = "Green"
                return "Switch to Green"
            elif input == "Emergency":
                return "Stay Red"
        elif self.state == "Green":
            if input == "Timer":
                self.state = "Yellow"
                return "Switch to Yellow"
            elif input == "Emergency":
                self.state = "Red"
                return "Emergency: Switch to Red"
        elif self.state == "Yellow":
            if input == "Timer":
                self.state = "Red"
                return "Switch to Red"
            elif input == "Emergency":
                self.state = "Red"
                return "Emergency: Switch to Red"
        return "Invalid Input"

# Usage
if __name__ == "__main__":
    light = TrafficLightDFA()
    print(light.transition("Timer"))      # Switch to Green
    print(light.transition("Emergency"))  # Emergency: Switch to Red
    print(light.transition("Timer"))      # Switch to Green
```

### 2. Non-Deterministic Finite Automaton (NFA)

An NFA allows multiple possible transitions for an input, simulating uncertainty
like a faulty timer that might skip Yellow.

- States: Red, Green, Yellow, Fault
- Inputs: Timer (T), Emergency (E)
- Transitions:
  - Red + Timer → {Green, Fault} (timer might fail)
  - Red + Emergency → Red
  - Green + Timer → {Yellow, Fault}
  - Green + Emergency → Red
  - Yellow + Timer → Red
  - Yellow + Emergency → Red
  - Fault + Timer → Red (reset)
  - Fault + Emergency → Red
- Start State: Red
- Accept State: None

```python
import random

class TrafficLightNFA:
    def __init__(self):
        self.state = "Red"
    
    def transition(self, input):
        if self.state == "Red":
            if input == "Timer":
                self.state = random.choice(["Green", "Fault"])
                return f"Switch to {self.state}"
            elif input == "Emergency":
                return "Stay Red"
        elif self.state == "Green":
            if input == "Timer":
                self.state = random.choice(["Yellow", "Fault"])
                return f"Switch to {self.state}"
            elif input == "Emergency":
                self.state = "Red"
                return "Emergency: Switch to Red"
        elif self.state == "Yellow":
            if input == "Timer":
                self.state = "Red"
                return "Switch to Red"
            elif input == "Emergency":
                self.state = "Red"
                return "Emergency: Switch to Red"
        elif self.state == "Fault":
            if input == "Timer":
                self.state = "Red"
                return "Reset to Red"
            elif input == "Emergency":
                self.state = "Red"
                return "Emergency: Switch to Red"
        return "Invalid Input"

# Usage
if __name__ == "__main__":
    light = TrafficLightNFA()
    print(light.transition("Timer"))      # Switch to Green or Fault
    print(light.transition("Timer"))      # Depends on state
    print(light.transition("Emergency"))  # Emergency: Switch to Red
```

### 3. Mealy Machine

A Mealy machine produces outputs based on the current state and input.
Outputs are instructions for drivers.

- States: Red, Green, Yellow
- Inputs: Timer (T), Emergency (E)
- Transitions and Outputs:
  - Red + Timer → Green, Output: "Go"
  - Red + Emergency → Red, Output: "Stop"
  - Green + Timer → Yellow, Output: "Prepare to Stop"
  - Green + Emergency → Red, Output: "Stop for Emergency"
  - Yellow + Timer → Red, Output: "Stop"
  - Yellow + Emergency → Red, Output: "Stop for Emergency"
- Start State: Red

```python
class TrafficLightMealy:
    def __init__(self):
        self.state = "Red"
    
    def transition(self, input):
        if self.state == "Red":
            if input == "Timer":
                self.state = "Green"
                return "Go"
            elif input == "Emergency":
                return "Stop"
        elif self.state == "Green":
            if input == "Timer":
                self.state = "Yellow"
                return "Prepare to Stop"
            elif input == "Emergency":
                self.state = "Red"
                return "Stop for Emergency"
        elif self.state == "Yellow":
            if input == "Timer":
                self.state = "Red"
                return "Stop"
            elif input == "Emergency":
                self.state = "Red"
                return "Stop for Emergency"
        return "Invalid Input"

# Usage
if __name__ == "__main__":
    light = TrafficLightMealy()
    print(light.transition("Timer"))      # Go
    print(light.transition("Timer"))      # Prepare to Stop
    print(light.transition("Emergency"))  # Stop for Emergency
```

### 4. Moore Machine

A Moore machine produces outputs based only on the current state.
Each state has a fixed output for drivers.

- States: Red, Green, Yellow
- Inputs: Timer (T), Emergency (E)
- State Outputs:
  - Red: "Stop"
  - Green: "Go"
  - Yellow: "Prepare to Stop"
- Transitions:
  - Red + Timer → Green
  - Red + Emergency → Red
  - Green + Timer → Yellow
  - Green + Emergency → Red
  - Yellow + Timer → Red
  - Yellow + Emergency → Red
- Start State: Red

```python
class TrafficLightMoore:
    def __init__(self):
        self.state = "Red"
    
    def get_output(self):
        outputs = {
            "Red": "Stop",
            "Green": "Go",
            "Yellow": "Prepare to Stop"
        }
        return outputs[self.state]
    
    def transition(self, input):
        if self.state == "Red":
            if input == "Timer":
                self.state = "Green"
            elif input == "Emergency":
                pass  # Stay Red
        elif self.state == "Green":
            if input == "Timer":
                self.state = "Yellow"
            elif input == "Emergency":
                self.state = "Red"
        elif self.state == "Yellow":
            if input == "Timer" or input == "Emergency":
                self.state = "Red"
        return self.get_output()

# Usage
if __name__ == "__main__":
    light = TrafficLightMoore()
    print(light.transition("Timer"))      # Go
    print(light.transition("Timer"))      # Prepare to Stop
    print(light.transition("Emergency"))  # Stop
```

These examples use a traffic light system to illustrate the differences
between DFA (predictable transitions), NFA (uncertain transitions),
Mealy (input-dependent outputs), and Moore (state-dependent outputs).
