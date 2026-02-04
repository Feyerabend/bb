
## Deontic Action Logic for Normatively Constrained Systems

*A Practical Guide for Software Engineers and Domain Experts*

This is a *semantic discipline* for capturing what *must*, *must not*,
and *may* happen in systems where rules matter—emergency response,
healthcare protocols, regulatory compliance, mission-critical operations.

*Core idea*: Normativity = selecting which possible futures are acceptable.

*Not*: A theorem-proving system or moral philosophy framework.

*Yes*: A rigorous way to translate client requirements into verifiable system constraints.


### Three Ways to Understand This System


#### Version 1: Intuitive (for stakeholders)

Think of your system as having many possible futures—different ways things could unfold.
Some of these futures are acceptable. Some are forbidden.

When you say "emergency responders must never travel more than 30 minutes,"
you're not writing code. You're *ruling out entire classes of futures* where that happens.

This formalism gives you a precise language to:
- State which futures are forbidden
- State which must happen if certain conditions hold
- Declare priorities when rules conflict
- Verify your system respects these boundaries


#### Version 2: Semi-Formal (for engineers)

We model normative constraints as a *partition over possible worlds*.

- Each "world" represents a complete trajectory or state of your system
- Admissible worlds = those that satisfy all applicable norms
- Norms are not inference rules; they are *filters* that reject worlds
- Priority ordering resolves conflicts without logical explosion

Your job as an engineer: translate domain rules into world-filtering predicates,
then verify your implementation produces only admissible executions.


### Version 3: Fully Formal (for verification specialists)

*Semantic structure*: ⟨W, A, V, ≻⟩ where:
- W is a non-empty set of possible worlds
- A ⊆ W is the admissible subset
- V: W × Prop → {⊤, ⊥} is a valuation function
- ≻ is a strict partial order over norms

*Interpretation*: Deontic operators quantify over A, not W.
Conditional norms restrict the quantification domain.
Priority ordering determines A when norms conflict.
No axiomatic closure over logical consequence.



### The Formal Core

#### Ontology

*Given*:
- W: A non-empty set of possible worlds
  - Each w ∈ W represents a complete system execution
    (state trajectory, event sequence, or static snapshot—your choice)
- A ⊆ W: The admissible worlds
  - This is THE normative boundary
  - Everything outside A is forbidden
  - Everything inside A is permitted

*Key Principle*: Normativity is world selection. That's it. No hidden commitments.

#### Operators (Syntax)

We define four primitive operators and two conditional forms:

*Primitive operators*:
- `O φ` — φ is obligatory
- `F φ` — φ is forbidden  
- `P φ` — φ is permitted
- `R φ` — φ is a requirement (constitutive invariant)

*Conditional operators*:
- `O(φ | ψ)` — φ is obligatory given ψ
- `F(φ | ψ)` — φ is forbidden given ψ

(Similar conditionals for P and R can be defined but are less common in practice.)


#### Semantics

Let V: W × Prop → {⊤, ⊥} be a valuation assigning truth values to propositions at worlds.


*Definition (Obligation)*:
```
⟦O φ⟧ = ⊤  iff  ∀w ∈ A: V(w, φ) = ⊤
```

In words: φ is obligatory iff φ holds in every admissible world.

*Definition (Prohibition)*:
```
⟦F φ⟧ = ⊤  iff  ∀w ∈ A: V(w, φ) = ⊥
```

In words: φ is forbidden iff φ is false in every admissible world.

*Semantic relation*: F φ ≡ O ¬φ (but not an axiom—just a theorem about our semantics)

*Definition (Permission)*:
```
⟦P φ⟧ = ⊤  iff  ∃w ∈ A: V(w, φ) = ⊤
```

In words: φ is permitted iff φ holds in at least one admissible world.

*Definition (Requirement)*:
```
⟦R φ⟧ = ⊤  iff  (∀w ∈ A: V(w, φ) = ⊤) ∧ (A ⊂ A')
```

where A' is the admissibility set if we remove the constraint φ.

In words: φ is a requirement iff it's obligatory AND it's not accidental—removing
it would expand what's admissible. This distinguishes invariants from derived consequences.

*Definition (Conditional Obligation)*:
```
⟦O(φ | ψ)⟧ = ⊤  iff  ∀w ∈ A: V(w, ψ) = ⊤ → V(w, φ) = ⊤
```

Equivalently: All admissible worlds where ψ holds are also worlds where φ holds.

*Key insight*: The condition ψ *filters* admissible worlds; it doesn't generate new ones.
This is for avoiding contrary-to-duty paradoxes.


#### Priority and Non-Monotonicity

*Core departure from classical deontic logic*: We reject monotonicity.

Let ≻ be a strict partial order over norms (think: priority levels).

*Admissibility under conflict*:

When norms conflict, A is constructed as follows:
1. Partition norms into priority levels
2. Start with the highest-priority norms
3. Include a world w in A iff it satisfies all maximal (highest unviolated) norms
4. Lower-priority norms may be violated if and only if respecting them would violate a higher-priority norm

*Formally*:
```
A = {w ∈ W | w satisfies all norms in Max(≻, w)}

where Max(≻, w) = {n ∈ Norms | ¬∃n' ∈ Norms: n' ≻ n ∧ w satisfies n'}
```

This is *semantic conflict resolution*, not syntactic.
It mirrors how real regulations and policies work.


#### What We Deliberately Exclude

*No closure under logical consequence*:
- Even if φ → ψ is valid, O φ does NOT entail O ψ
- This is intentional: we describe what's obligatory, not what follows from it

*No baked-in axioms like*:
- O φ → P φ (obligation implies permission)
- O φ → ¬O ¬φ (deontic consistency)
- O(φ ∧ ψ) → O φ (distributivity)

These may be *semantically valid* in many models we construct,
but they're not axioms of the calculus. We discover them, we don't assume them.

*Why?* We want a *descriptive* tool, not a prescriptive logical system.
The formalism adapts to the domain, not vice versa.



### How the System Actually Works

#### Step 1: Define Your World Structure

*Question*: What does a "world" mean for your system?

*Options*:
- *Static state*: A snapshot (e.g., database state, configuration)
- *Trajectory*: A complete execution trace (e.g., event log, temporal sequence)
- *Hybrid*: State + next-action possibilities

*Example* (emergency dispatch):
```
A world w is a complete 24-hour execution trace containing:
  - All emergency events
  - All responder assignments
  - All travel times
  - All status transitions
```


#### Step 2: Define Your Propositions

*Question*: What properties can we check at/across worlds?

*Examples*:
```
response_time(incident_id) ≤ 30 minutes
assigned_responders(incident_id) ≥ 2
vehicle_capacity(vehicle_id) ≥ passenger_count
responder_certified(responder_id, incident_type)
```

These become your atomic propositions φ, ψ, etc.


#### Step 3: Encode Your Norms

*For each domain rule*, choose the appropriate operator:

*Use `O φ` when*: Every acceptable outcome must have φ
```
O(response_time ≤ 30)
"We must always respond within 30 minutes"
```

*Use `F φ` when*: No acceptable outcome has φ
```
F(uncertified_assignment)
"We must never assign uncertified responders"
```

*Use `P φ` when*: At least one acceptable outcome has φ (rare in practice)
```
P(overtime_authorized)
"Overtime is permitted (but not required)"
```

*Use `R φ` when*: φ is a constitutive invariant, not a derived property
```
R(battery_level > 0)
"Devices must always have power (this isn't negotiable)"
```

*Use `O(φ | ψ)` when*: φ is required only when ψ holds
```
O(hazmat_team_present | chemical_incident)
"Hazmat team is required if and only if it's a chemical incident"
```


#### Step 4: Specify Priorities

*Question*: Which norms override which?

*Syntax*:
```
n₁ ≻ n₂  means  "norm n₁ has higher priority than n₂"
```

*Example*:
```
CRITICAL: R(no_responder_injury)
HIGH:     O(response_time ≤ 30)
MEDIUM:   O(minimize_cost)
```

Encoded as:
```
no_responder_injury ≻ response_time ≻ minimize_cost
```

*Semantics*: If satisfying response_time would risk injury,
the system is permitted to violate response_time.
But it must still respect no_responder_injury.


#### Step 5: Compute Admissibility

*Algorithm* (conceptual):

```
A = W  // start with all possible worlds

for each priority level p in descending order:
    for each norm n at level p:
        A = A ∩ {w | w satisfies n}
        if A becomes empty:
            relax lower-priority norms until A is non-empty
```

*In practice*: This becomes a constraint satisfaction or model-checking problem.


#### Step 6: Verification

*Questions to check*:

1. *Consistency*: Is A non-empty? (Do any admissible futures exist?)
2. *Satisfiability*: Can your implementation produce trajectories in A?
3. *Coverage*: Does every possible input/scenario have an admissible response?
4. *No false positives*: Does your implementation ever produce trajectories outside A?

*Tools*: Model checkers (TLA+, Alloy), SAT solvers, runtime monitors.



### Practical Guide for Programmers

#### When to Use This Formalism

*Good fit*:
- Healthcare protocols (drug interactions, dosing rules)
- Emergency response (dispatch rules, resource allocation)
- Financial compliance (trading restrictions, audit requirements)
- Safety-critical systems (aviation, nuclear, automotive)
- Access control and authorization
- Workflow management with strict sequencing rules

*Poor fit*:
- User preference optimisation (use utility functions instead)
- Pure performance tuning (no hard constraints)
- Statistical/ML systems (no crisp rule boundaries)


#### Translation Workflow

*From requirements document to formal norms*:

1. *Extract modal statements*:
   Look for "must," "must not," "may," "required," "prohibited," "only if"

2. *Identify conditions*:
   Look for "when," "if," "unless," "during," "after"

3. *Determine priority*:
   Ask domain experts about conflict scenarios

4. *Formalise incrementally*:
   ```
   Requirement: "During peak hours, never assign the same ambulance 
                 to overlapping emergencies unless critical shortage."
   
   Step 1: Define propositions
     peak_hours(t)
     overlapping_assignment(ambulance_id, t)
     critical_shortage(t)
   
   Step 2: Identify operator
     This is a conditional prohibition with an exception
   
   Step 3: Formalise
     High priority:  F(overlapping_assignment | peak_hours ∧ ¬critical_shortage)
     Override:       critical_shortage ≻ no_overlap
   ```

5. *Validate with domain expert*:
   Show formalisation, ask about edge cases


#### Implementation Patterns

*Pattern 1: Static Verification*

Generate all reachable states (or a representative sample), check whether they're all in A.

```python
def verify_admissibility(system_model, norms):
    admissible_worlds = apply_norms(all_possible_worlds, norms)
    reachable_worlds = system_model.get_reachable_states()
    
    violations = reachable_worlds - admissible_worlds
    if violations:
        return ViolationReport(violations)
    return Success()
```

*Pattern 2: Runtime Monitoring*

Track the current execution, reject actions that would lead outside A.

```python
class NormativeMonitor:
    def __init__(self, norms, priority_order):
        self.norms = norms
        self.priorities = priority_order
        self.current_world = initial_state
    
    def check_action(self, proposed_action):
        future_world = self.simulate(self.current_world, proposed_action)
        
        for priority_level in self.priorities:
            for norm in priority_level:
                if not norm.satisfied_by(future_world):
                    if norm.priority == 'CRITICAL':
                        raise NormViolation(norm, proposed_action)
                    else:
                        log_warning(norm, proposed_action)
        
        return Allowed()
```

*Pattern 3: Generative (planning)*

Only generate actions that keep you in A.

```python
def generate_admissible_plan(initial_state, goal, norms):
    search_space = {s for s in reachable(initial_state) 
                    if all_norms_satisfied(s, norms)}
    return shortest_path(initial_state, goal, search_space)
```

#### Testing Norms

*Create a test suite that checks*:

1. *Positive cases*: Scenarios that should be admissible
2. *Negative cases*: Scenarios that should be forbidden
3. *Boundary cases*: Exactly at thresholds
4. *Conflict cases*: When norms compete
5. *Conditional cases*: When conditions toggle norms on/off

```python
def test_response_time_norm():
    norm = O(response_time <= 30)
    
    # Should pass
    assert norm.satisfied_by(world_with_response_time(25))
    
    # Should fail
    assert not norm.satisfied_by(world_with_response_time(35))
    
    # Boundary
    assert norm.satisfied_by(world_with_response_time(30))
```

#### Common Pitfalls

*Pitfall 1: Over-constraint*
- *Symptom*: A = ∅ (no admissible worlds)
- *Fix*: Review conflicts, adjust priorities, or relax lower-priority norms

*Pitfall 2: Vacuous conditionals*
- *Symptom*: O(φ | ψ) is trivially true because ψ never holds
- *Fix*: Check your condition coverage

*Pitfall 3: Implicit transitivity*
- *Mistake*: Assuming O φ and φ → ψ gives you O ψ
- *Fix*: If you want O ψ, state it explicitly

*Pitfall 4: Confusing permission with obligation*
- *Mistake*: Encoding "X may happen" as O(X) instead of P(X)
- *Fix*: Use the weakest operator that captures intent



### Practical Guide for Domain Experts

#### Your Role

You are the *source of truth* about what's acceptable and what isn't.

The formalism is a translation tool, not a substitute for your judgment.

#### How to Specify Norms

*Template 1: Unconditional Obligation*
```
"We must always _____"
→ O(proposition)

Example: "We must always verify patient identity before administering medication"
→ O(identity_verified_before_medication)
```

*Template 2: Unconditional Prohibition*
```
"We must never ______"
→ F(proposition)

Example: "We must never exceed maximum dosage"
→ F(dosage > maximum_safe_dosage)
```

*Template 3: Conditional Obligation*
```
"If ___ then we must ___"
"When ___ we must ___"
"During ___ it is required that ___"
→ O(action | condition)

Example: "If a patient has a penicillin allergy, we must avoid all beta-lactam antibiotics"
→ O(no_beta_lactam | penicillin_allergy)
```

*Template 4: Conditional Prohibition*
```
"If ___ then we must never ___"
"During ___ it is forbidden to ___"
→ F(action | condition)

Example: "During pregnancy, NSAIDs are contraindicated in the third trimester"
→ F(prescribe_nsaid | pregnant ∧ third_trimester)
```

*Template 5: Requirement (Invariant)*
```
"It is absolutely required that ___"
"___ is non-negotiable"
"System integrity depends on ___"
→ R(proposition)

Example: "Patient consent is always required before treatment"
→ R(consent_obtained_before_treatment)
```

#### How to Specify Priorities

*Questions to ask yourself*:

1. If rules X and Y conflict, which wins?
2. What are we willing to sacrifice to preserve what?
3. Which rules are "hard constraints" vs "optimisation goals"?

*Priority levels* (example hierarchy):

```
TIER 1: Safety-critical (life, safety, legal mandates)
  Example: No untrained personnel in hazardous zones

TIER 2: Operational requirements (mission success, service level)
  Example: Response within 30 minutes

TIER 3: Optimization goals (cost, efficiency, convenience)
  Example: Minimize fuel consumption
```

*Exercise*: Present a conflict scenario

```
Scenario: It's peak hours. All ambulances are assigned. 
A new critical emergency comes in.

Conflicting norms:
  - O(response_time ≤ 30)
  - F(overlapping_assignment | peak_hours)

Question: Which rule breaks?
Answer determines priority.
```

#### Red Flags (When to Push Back)

*Red flag 1*: Engineer says "That's logically impossible"
- *Response*: Maybe the formalization is wrong. Let's check if we captured your intent correctly.

*Red flag 2*: System frequently violates "must never" rules
- *Response*: Either the rule is wrong, or the system is broken. Which is it?

*Red flag 3*: Priority conflicts are unresolved
- *Response*: Domain experts must decide. Engineers can't guess.

*Red flag 4*: "The system can't check that"
- *Response*: Then we need instrumentation, or a different architecture. Don't weaken the norm.



### Advanced Topics

#### Embedding Temporal Logic

For systems where time matters, extend worlds to be temporal structures:

```
w = (S, <, L)
where:
  S = set of time points
  < = temporal ordering
  L: S → 2^Prop (labeling function)
```

Then norms can quantify over time:

```
O(□ φ)          "φ must always hold"
O(◇ φ)          "φ must eventually hold"
O(φ U ψ)        "φ until ψ"
F(◇ φ)          "φ must never occur"
```

This is TLA+ territory. Existing model checkers can verify these directly.

#### Relating to Alloy

Alloy is a natural implementation target:

```alloy
sig World {
  // your domain model
}

pred Admissible[w: World] {
  // conjunction of all maximal norms
  all norms in HighPriority | norm.satisfied[w]
  // lower priority norms as soft constraints
}

run Admissible for 5 World
```

The Alloy Analyzer will find admissible worlds (or prove none exist).

#### Handling Contrary-to-Duty

*Problem*: "If you violate norm X, you must do Y."

*Example*: "You must not speed. But if you do speed, you must pay a fine."

*Classical formalisation* (broken):
```
O(¬speed)
O(speed → fine)
```

This explodes: if you speed, you're in a forbidden world,
so everything is obligatory/forbidden.

*Our approach*:

Use priority and conditional norms:

```
Priority 1: F(speed)
Priority 2: O(fine | speed)
```

Semantics:
- Speeding worlds are inadmissible at priority 1
- But IF we relax priority 1 (for analysis), THEN among speeding worlds,
  only those with fines are admissible at priority 2

This lets you reason about "what should happen if the ideal is violated" without paradox.

#### Probabilistic Extensions

Some norms are statistical:

"At least 90% of emergencies must be responded to within 30 minutes."

Extend to:

```
O₀.₉(response_time ≤ 30)
```

Semantics:
```
⟦O_p(φ)⟧ = ⊤  iff  μ({w ∈ A | V(w, φ) = ⊤}) ≥ p
```

where μ is a measure over A.

Requires a probability distribution over admissible worlds, but otherwise straightforward.

#### Multi-Agent Norms

When multiple agents have norms:

```
O_agent1(φ)      "Agent 1 is obligated to ensure φ"
O_agent2(ψ)      "Agent 2 is obligated to ensure ψ"
```

Semantics: A world is admissible iff each agent's norms are satisfied within their scope of control.

This requires partitioning the world into agent-controlled variables.



### What This System Is and Isn't

#### What It Is

- *A semantic framework* for world selection under normative constraints
- *A specification language* for translating domain rules into verifiable predicates  
- *A bridge* between regulatory requirements and formal verification  
- *An engineering discipline* grounded in possible-worlds semantics  
- *A conflict-resolution mechanism* via priority ordering  

#### What It Isn't

- *A moral philosophy*: We don't tell you what *should* be obligatory, only how to formalize what you've decided  
- *A legal reasoning system*: Laws are interpreted by humans; this helps formalize the results  
- *A complete deontic logic*: We deliberately omit closure properties and axiomatic commitments  
- *An AI ethics framework*: That's a different (and much harder) problem  
- *A replacement for human judgment*: It's a tool to clarify and verify judgment, not supplant it  

#### When It Succeeds

You'll know this system is working when:

- *Stakeholders recognize their rules* in the formalization
- *Conflicts become visible* before deployment, not during incidents
- *Verification tools* can check your implementation against norms
- *Audits trace back* to explicit normative choices
- *Changes propagate clearly* from policy to code

#### When It Fails

This system won't help if:

- *Requirements are fundamentally unclear*: Formalisation can't fix ambiguity in your rules (but it can expose it)
- *The domain changes faster than you can model it*: Some systems are too fluid for static norms
- *Stakeholders can't agree on priorities*: We give you tools to encode decisions, not make them
- *You need probabilistic reasoning under uncertainty*: This is about crisp constraints, not Bayesian inference




### Worked Example: Emergency Dispatch
#### Domain

Emergency dispatch system managing ambulances, fire trucks, and paramedics responding to 911/112 calls.

#### Step 1: Define Worlds

A world w is a complete 24-hour execution trace containing:
- Set of incidents: I = {i₁, i₂, ...}
- Set of responders: R = {r₁, r₂, ...}
- Assignment function: assign: I → 2^R
- Timing function: response_time: I → ℕ (minutes)
- Certification: certified: R × IncidentType → Bool
- Availability: available: R × Time → Bool

#### Step 2: Define Propositions

```
fast_response(i) ≜ response_time(i) ≤ 30
proper_cert(i) ≜ ∀r ∈ assign(i): certified(r, type(i))
adequate_crew(i) ≜ |assign(i)| ≥ min_crew(type(i))
no_overload(r) ≜ |{i | r ∈ assign(i) ∧ overlaps(i)}| ≤ 1
responder_safe(r) ≜ ¬injured(r) ∧ equipment_ok(r)
```

#### Step 3: Encode Norms

**From requirements document**:

1. "Responders must never be put in unsafe conditions"  
   → `R(∀r ∈ R: responder_safe(r))`  
   Priority: CRITICAL

2. "All responses must arrive within 30 minutes"  
   → `O(∀i ∈ I: fast_response(i))`  
   Priority: HIGH

3. "Only certified personnel may respond to specialized incidents"  
   → `O(∀i ∈ I: proper_cert(i))`  
   Priority: HIGH

4. "Each incident requires minimum crew size"  
   → `O(∀i ∈ I: adequate_crew(i))`  
   Priority: MEDIUM

5. "Responders should not be double-booked"  
   → `O(∀r ∈ R: no_overload(r))`  
   Priority: LOW

6. "In mass casualty events, double-booking is permitted"  
   → `mass_casualty ≻ no_overload`

#### Step 4: Admissibility Computation

```
Priority levels:
  CRITICAL: responder_safe
  HIGH: fast_response, proper_cert
  MEDIUM: adequate_crew
  LOW: no_overload

A = {w ∈ W | w satisfies all CRITICAL norms}
    ∩ {w ∈ W | w satisfies all HIGH norms or CRITICAL requires violation}
    ∩ {w ∈ W | w satisfies all MEDIUM norms or higher priority requires violation}
    ∩ {w ∈ W | w satisfies all LOW norms or higher priority requires violation}
```

#### Step 5: Conflict Scenarios

*Scenario 1*: Rush hour, all units busy, new critical incident

Conflict: `fast_response` vs `no_overload`

Resolution: `fast_response` has higher priority → double-booking is permitted

*Scenario 2*: Only uncertified responders available for hazmat incident

Conflict: `fast_response` vs `proper_cert`

Resolution: Both are HIGH priority → A = ∅ → system must escalate to external resources

*Scenario 3*: Budget cuts reduce crew size below minimum

Conflict: `adequate_crew` vs resource availability

Resolution: This is a systemic violation, not a runtime conflict → operational failure, must be fixed at planning level

#### Step 6: Implementation

```python
class DispatchSystem:
    def __init__(self, norms, priorities):
        self.norms = norms
        self.priorities = priorities
    
    def assign_responders(self, incident):
        candidates = self.available_responders(incident)
        
        # Filter by CRITICAL norms (non-negotiable)
        safe_candidates = [r for r in candidates if self.is_safe(r, incident)]
        
        # Filter by HIGH norms (certification)
        certified_candidates = [r for r in safe_candidates 
                                if self.is_certified(r, incident.type)]
        
        if not certified_candidates:
            raise EscalationRequired("No certified responders available")
        
        # Try to satisfy MEDIUM norms (crew size)
        assignment = self.select_crew(certified_candidates, incident.min_crew)
        
        # Check LOW norms (no overload), relax if necessary
        if not self.check_overload(assignment):
            if incident.priority == 'CRITICAL':
                log_warning("Double-booking permitted due to critical incident")
            else:
                # Try to find alternative that doesn't violate
                assignment = self.rebalance_or_wait(assignment, incident)
        
        return assignment
```

#### Step 7: Verification

*Test case 1*: Normal operations
```python
def test_normal_dispatch():
    system = DispatchSystem(norms, priorities)
    incident = Incident(type='medical', priority='routine')
    assignment = system.assign_responders(incident)
    
    assert all(r.is_safe for r in assignment)
    assert all(r.certified_for(incident.type) for r in assignment)
    assert len(assignment) >= incident.min_crew
    assert no_double_booking(assignment)
```

*Test case 2*: Conflict scenario
```python
def test_critical_during_rush_hour():
    system = DispatchSystem(norms, priorities)
    # Set up scenario where all responders are assigned
    system.assign_all_to_routine_incidents()
    
    critical_incident = Incident(type='cardiac_arrest', priority='CRITICAL')
    assignment = system.assign_responders(critical_incident)
    
    # Should permit double-booking
    assert len(assignment) > 0
    assert all(r.is_safe for r in assignment)
    assert all(r.certified_for(critical_incident.type) for r in assignment)
    # no_overload may be violated - that's OK given priority
```



### Next Steps

#### For immediate use

1. *Identify your domain*: What system are you formalizing?
2. *List your norms*: Gather all "must," "must not," "should" statements
3. *Define world structure*: What does a complete execution/state look like?
4. *Formalize incrementally*: Start with 3-5 critical norms, expand from there
5. *Validate with stakeholders*: Confirm formalizations match intent
6. *Choose verification tools*: Model checker, SAT solver, runtime monitor, or custom
7. *Implement and test*: Build, verify, deploy

#### For deeper integration

- *Temporal embedding*: Integrate with TLA+ or LTL for temporal properties
- *Alloy modeling*: Use Alloy Analyzer for automated instance-finding
- *Runtime monitoring*: Build enforcement hooks into your system
- *Traceability*: Link norms back to requirements documents and regulations
- *Change management*: Version your norms alongside your code

#### For theoretical extensions

- Probabilistic norms for statistical requirements
- Multi-agent settings with overlapping jurisdictions
- Epistemic extensions for knowledge-dependent norms
- Revision operators for norm evolution
- Proof-carrying code with normative certificates



### Conclusion

This system lives at the boundary between logic and engineering,
between philosophy and software, between "what should be" and "what will be."

It doesn't solve every problem. It won't replace human judgment. It won't make hard decisions easy.

What it *will* do:

- Make your normative commitments *explicit*
- Make conflicts *visible* before they become incidents
- Make verification *possible* where it was previously informal
- Make responsibility *traceable* from policy to implementation

If that's what you need, this formalism will serve you well.

If you need more, extend it. If you need less, simplify it.
But start here: with worlds, admissibility, and the honest question:
*Which futures are we willing to accept?*





### Relation to Prior Work

#### Von Wright and Kanger

*What we take*:
- Possible-worlds semantics for deontic operators
- Norms as world-filters rather than inference rules
- Conditional norms via domain restriction

*What we modify*:
- No commitment to axiom schemas (D, K, etc.)
- Explicit priority mechanisms (not in original systems)
- Engineering focus over philosophical completeness

### Standard Deontic Logic (SDL)

*Where we depart*:
- We reject monotonicity (norm conflicts are real, not paradoxes)
- We avoid closure under logical consequence (too strong for practical use)
- We don't adopt O φ → P φ as an axiom (want to discover it, not assume it)

*Why*:
SDL is designed for philosophical analysis. We need a tool for *systems engineering*.

The classic paradoxes (Ross, Good Samaritan, Chisholm) don't arise here because
we don't have free inference rules—we only have semantic interpretation.

### Temporal Logic (TLA+, LTL)

*Relationship*:
- TLA+ is a specification language; this is a normative layer on top
- LTL formulas can be embedded as propositions in our operators
- Norms constrain which TLA+ behaviors are acceptable

*Integration*:
```
TLA+ spec defines: all possible behaviors
Our norms define: which behaviors are admissible
Model checker verifies: implementation ⊆ admissible behaviors
```

### Alloy

*Relationship*:
- Alloy finds instances of relational models
- Our norms become Alloy predicates
- Admissible worlds = Alloy instances satisfying the admissibility predicate

*Workflow*:
1. Model domain in Alloy
2. Translate norms to predicates
3. Use Alloy Analyzer to check satisfiability
4. Generate test cases from found instances

