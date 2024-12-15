class PushdownAutomaton:
    def __init__(self):
        self.stack = []
        self.state = "q0"  # start state

    def transition(self, state, symbol):
        if state == "q0":
            if symbol == 'a':
                self.stack.append('A')
                return "q0"  # stay in q0 while reading a's
            elif symbol == 'b' and self.stack:
                self.stack.pop()
                return "q1"  # transition to q1 when reading the first b
        elif state == "q1":
            if symbol == 'b' and self.stack:
                self.stack.pop()
                return "q1"  # stay in q1 while reading b's
        return None  # invalid state or transition

    def accepts(self, input_string):
        self.stack = []
        self.state = "q0"

        for symbol in input_string:
            self.state = self.transition(self.state, symbol)
            if self.state is None:
                return False  # invalid transition or stack mismatch

        # accept if in final state and stack is empty
        return self.state == "q1" and not self.stack


# test
pda = PushdownAutomaton()
print(pda.accepts("aabb"))    # True, valid balanced string
print(pda.accepts("aaabbb"))  # True, valid balanced string
print(pda.accepts("abab"))    # False, invalid order
print(pda.accepts("aab"))     # False, unbalanced string
print(pda.accepts("baab"))     # False, invalid order
