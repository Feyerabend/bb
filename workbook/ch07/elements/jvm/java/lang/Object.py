class Object:
    def __init__(self):
        # Optional: Map to Python __init__ if needed, but use <init> for JVM naming
        pass

    def __init__(self):  # Redundant, but for Python instantiation if used directly
        pass

    # JVM constructor (no-op)
    def __init__(self):
        pass  # No-op, like Java

    # Minimal implementations for common methods (add more as needed)
    def equals(self, other):
        return self is other

    def hashCode(self):
        return id(self)  # Python equivalent of reference hash

    def toString(self):
        return f"{self.__class__.__name__}@{hex(id(self))}"

    # Synchronization methods (stubbed; full impl needs threading support)
    def notify(self):
        pass  # Raise NotImplementedError if needed

    def notifyAll(self):
        pass

    def wait(self, *args):
        pass

    # Clone (requires Cloneable; stub)
    def clone(self):
        raise Exception("CloneNotSupportedException")

    # Finalize (GC hook; ignore)
    def finalize(self):
        pass

    # getClass (return class name as string, since no Class obj yet)
    def getClass(self):
        return self.__class__.__name__
