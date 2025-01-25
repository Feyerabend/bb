
class Variable:
    _id = 1
    def __init__(self, name=None):
        self.name = name or f"V{Variable._id}"
        Variable._id += 1
    def __repr__(self): return self.name

class Term:
    def __init__(self, functor, args=None):
        self.functor = functor
        self.args = args or []
    
    def __repr__(self):
        if not self.args:
            return self.functor
        return f"{self.functor}({', '.join(map(repr, self.args))})"

class Clause:
    def __init__(self, head, body=None):
        self.head = head
        self.body = body if body else Term('true')

class PrologEngine:
    def __init__(self, clauses):
        self.clauses = clauses
        self.choice_points = []
    
    def solve(self, goal):
        return self._prove(goal, {}, 0)
    
    def _prove(self, goal, subst, depth):
        if isinstance(goal, Term) and goal.functor == ',' and goal.args:
            yield from self._prove_conjunction(goal.args, subst, depth)
            return
        
        for clause in self.clauses:
            fresh_clause = self._freshen(clause, depth)
            new_subst = self.unify(goal, fresh_clause.head, subst.copy())
            if new_subst is None: continue
            
            self.choice_points.append((clause, depth))
            try:
                if fresh_clause.body.functor == 'true':
                    yield new_subst
                else:
                    yield from self._prove(fresh_clause.body, new_subst, depth+1)
            finally:
                self.choice_points.pop()
    
    def _prove_conjunction(self, goals, subst, depth):
        if not goals:
            yield subst
            return
        first, *rest = goals
        for subst1 in self._prove(first, subst, depth):
            yield from self._prove_conjunction(rest, subst1, depth)
    
    def _freshen(self, clause, depth): # help rename variables
        mapping = {}
        def fresh_term(t):
            if isinstance(t, Variable):
                return mapping.setdefault(t.name, Variable())
            if isinstance(t, Term):
                return Term(t.functor, [fresh_term(a) for a in t.args])
            return t
        return Clause(fresh_term(clause.head), fresh_term(clause.body))
    
    def unify(self, x, y, subst):
        x = self.walk(x, subst)
        y = self.walk(y, subst)
        
        if x == y: return subst
        if isinstance(x, Variable): return self.extend(subst, x, y)
        if isinstance(y, Variable): return self.extend(subst, y, x)
        if isinstance(x, Term) and isinstance(y, Term):
            if x.functor == y.functor and len(x.args) == len(y.args):
                for xa, ya in zip(x.args, y.args):
                    subst = self.unify(xa, ya, subst)
                    if subst is None: break
                return subst
        return None
    
    def walk(self, term, subst):
        while isinstance(term, Variable) and term in subst:
            term = subst[term]
        return term
    
    def extend(self, subst, var, val):
        if self.occurs(var, val, subst): return None
        new_subst = subst.copy()
        new_subst[var] = val
        return new_subst
    
    def occurs(self, var, term, subst):
        term = self.walk(term, subst)
        if var == term: return True
        if isinstance(term, Term): return any(self.occurs(var, a, subst) for a in term.args)
        return False

def list_term(elements): # helper create a Prolog list
    l = Term('[]')
    for e in reversed(elements):
        l = Term('.', [e, l])
    return l

def format_term(term):
    if isinstance(term, Term) and term.functor == '.':
        elements = []
        while isinstance(term, Term) and term.functor == '.' and len(term.args) == 2:
            elements.append(format_term(term.args[0]))
            term = term.args[1]
        if isinstance(term, Term) and term.functor == '[]':
            return f"[{', '.join(map(str, elements))}]"
        else:
            return f"[{', '.join(map(str, elements))} | {format_term(term)}]"
    elif isinstance(term, Term):
        return f"{term.functor}({', '.join(map(format_term, term.args))})" if term.args else term.functor
    else:
        return str(term)

# append implementation
if __name__ == "__main__":

    H, T, X, Y, Z = Variable('H'), Variable('T'), Variable('X'), Variable('Y'), Variable('Z')
    

    database = [
        # Base case: append([], Y, Y)
        Clause(Term('append', [Term('[]'), Y, Y])),
        
        # Recursive case: append([H|T], Y, [H|Z]) :- append(T, Y, Z)
        Clause(Term('append', [Term('.', [H, T]), Y, Term('.', [H, Z])]), 
               Term('append', [T, Y, Z]))
    ]
    
    engine = PrologEngine(database)
    
    def run_query(term):
        print(f"\nQuery: {term}")
        seen = set()
        for solution in engine.solve(term):
            result = substitute(term, solution)
            result_str = str(result)
            if result_str not in seen:
                seen.add(result_str)
                print(f"  {format_term(result)}")
                #print(f"  {result}")
    
    def substitute(term, subst):
        term = engine.walk(term, subst)
        if isinstance(term, Variable):
            return term
        if isinstance(term, Term):
            return Term(term.functor, [substitute(a, subst) for a in term.args])
        return term
    
    # Test
    L1, L2, L3 = list_term([1,2]), list_term([3,4]), list_term([1,2,3,4])
    
    # Basic append
    run_query(Term('append', [L1, L2, X]))
    
    # Split list
    run_query(Term('append', [X, Y, L3]))
    
    # Find prefix
    run_query(Term('append', [X, list_term([3,4]), L3]))
    
    # Find suffix
    run_query(Term('append', [list_term([1,2]), Y, L3]))
    
    # Empty list cases
    run_query(Term('append', [Term('[]'), Term('[]'), X]))
    run_query(Term('append', [X, Y, Term('[]')]))
