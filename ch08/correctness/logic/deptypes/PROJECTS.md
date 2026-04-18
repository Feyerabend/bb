
## Projects on Dependent Types

### 1. Smart Contract Validator

- A DSL where contract terms (dates, amounts, parties) become type parameters  
- Type-driven proofs that:  
  ```python
  def transfer(amount: Money, 
               from: AccountWith(MinBalance(amount)), 
               to: Account) -> Contract:
      # Compiles only if 'from' has ≥ amount
  ```  
- Automated detection of:  
  - Time paradoxes (obligations before effective dates)
  - Impossible conditions (X must happen if Y doesn't, but Y always happens)


### 2. Biological Sequence Analyzer

- DNA/RNA sequences with length-encoded types:  
  ```python
  def PCR_primers(forward: DNASeq[18-22bp], 
                  reverse: DNASeq[18-22bp], 
                  template: DNASeq[L]) -> Amplicon[L]:
      # Enforces matching Tm, GC%, and length constraints
  ```  
- Type-safe operations:  
  - Restriction enzyme cutting (proves recognition sites exist)  
  - Frame-aware protein translation (codon groups of 3)  


### 3. Industrial Control System

- Sensor readings with calibrated ranges:  
  ```python
  def activate_valve(
      temp: SensorReading[0-100°C], 
      pressure: SensorReading[P > 2bar]
  ) -> ActuatorCommand[SafeState]:
  ```  
- Machine state transitions proven at compile time:  
  ```python
  typecheck(Idle → Heating → Mixing → Packaging)  # Valid
  typecheck(Idle → Packaging)                     # Fails!
  ```  

### 4. Formal Proof Checker

- A natural deduction system where:  
  ```python
  def modus_ponens(
      p_implies_q: Proof[P → Q], 
      p: Proof[P]
  ) -> Proof[Q]: ...
  ```  
- Logical contradictions become type errors:  
  ```python
  Proof[P ∧ ¬P]  # Immediately fails type checking
  ```  
- Supports automated induction proofs over Peano naturals
- Help: Start of a limited [proof checker](./03/) for natural deduction


### 5. Game Mechanics Verifier

- RPG rules with type-enforced invariants:  
  ```python
  def cast_spell(
      caster: Character[Mana ≥ spell_cost],
      target: ValidTarget[spell_type]
  ) -> BattleLog[DamageDealt ∨ StatusApplied]:
  ```  
- Proves at compile time that:  
  - No skill trees have dead-end upgrades  
  - All quests are completable with available items  
  - Damage calculations never overflow health pools  


### Advantages

1. Correct-by-Construction – Bugs become type errors  

2. Self-Documenting – Types encode business/scientific rules  

3. Extensible Proofs – Add new constraints without runtime checks  

