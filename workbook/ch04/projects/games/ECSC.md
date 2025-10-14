### Entity-Component-System (ECS) Architecture: A Comprehensive Guide for Large-Scale Games


#### Table of Contents
1. [Introduction](#introduction)
2. [Pseudo-code Syntax Guide](#pseudo-code-syntax-guide)
3. [Core Concepts](#core-concepts)
4. [Complete Pseudo-code Implementation](#complete-pseudo-code-implementation)
5. [Advanced Patterns](#advanced-patterns)
6. [Extension Roadmap](#extension-roadmap)
7. [Performance Optimization](#performance-optimization)
8. [Real-World Examples](#real-world-examples)


#### Pseudo-code Syntax Guide

This guide uses C++-inspired pseudo-code. Here's a quick reference for the syntax:

##### Basic Data Structures

```pseudo

// ARRAYS (Fixed or Dynamic Lists)


// Declaration
array<Type> myArray

// Examples
array<int> numbers = [1, 2, 3, 4, 5]
array<string> names = ["Alice", "Bob", "Charlie"]
array<Entity> entities

// Access
value = myArray[index]        // Get element at index
myArray[index] = newValue     // Set element at index

// Operations
myArray.add(item)             // Add to end
myArray.remove(index)         // Remove at index
myArray.size()                // Get length
myArray.isEmpty()             // Check if empty

// Real-world equivalent:
// C++:        std::vector<Type>
// JavaScript: Array or Type[]
// Python:     list
// C#:         List<Type>



// MAPS (Key-Value Pairs / Dictionaries)


// Declaration
map<KeyType, ValueType> myMap

// Examples
map<string, int> scores
map<int, string> playerNames
map<EntityID, Component> components

// Usage
scores["Alice"] = 100                    // Set value
score = scores["Alice"]                  // Get value
scores.remove("Alice")                   // Remove entry
exists = "Alice" in scores               // Check if key exists
exists = scores.contains("Alice")        // Alternative check

// Iteration
for key, value in myMap:
    print(key + ": " + value)

// Real-world equivalent:
// C++:        std::map<K,V> or std::unordered_map<K,V>
// JavaScript: Object {} or Map
// Python:     dict
// C#:         Dictionary<K,V>



// SETS (Unique Collections)


// Declaration
set<Type> mySet

// Examples
set<EntityID> entities
set<string> tags

// Usage
mySet.add(item)              // Add item (no duplicates)
mySet.remove(item)           // Remove item
exists = item in mySet       // Check if exists
mySet.contains(item)         // Alternative check
mySet.size()                 // Get count

// Real-world equivalent:
// C++:        std::set<T> or std::unordered_set<T>
// JavaScript: Set
// Python:     set
// C#:         HashSet<T>



// QUEUES (FIFO - First In First Out)


// Declaration
queue<Type> myQueue

// Examples
queue<Event> eventQueue
queue<EntityID> processingQueue

// Usage
myQueue.enqueue(item)        // Add to back
item = myQueue.dequeue()     // Remove from front
item = myQueue.peek()        // View front without removing
myQueue.isEmpty()            // Check if empty

// Real-world equivalent:
// C++:        std::queue<T>
// JavaScript: Array with push/shift
// Python:     collections.deque
// C#:         Queue<T>



// LISTS (Ordered Collections)


// Declaration
list<Type> myList

// Examples
list<System> systems
list<Objective> objectives

// Usage (similar to arrays but may be linked lists)
myList.add(item)             // Add to end
myList.insert(index, item)   // Insert at position
myList.remove(item)          // Remove by value
myList.removeAt(index)       // Remove by index

// Real-world equivalent:
// C++:        std::list<T>
// JavaScript: Array
// Python:     list
// C#:         List<T>
```

##### Practical Examples with Explanations

```pseudo

// EXAMPLE 1: Animation Storage


class AnimationComponent:
    string currentAnimation              // e.g., "walk", "run", "jump"
    float frameTime                      // Time spent on current frame
    int currentFrame                     // Which frame we're on (0, 1, 2...)
    map<string, Animation> animations    // DICTIONARY of animations

// What map<string, Animation> means:
// - KEY: animation name (string) like "walk", "run", "idle"
// - VALUE: Animation object containing frames, speed, etc.

// How to use it:
animComp = new AnimationComponent()

// Store animations by name
animComp.animations["walk"] = new Animation(
    frames: ["walk_01.png", "walk_02.png", "walk_03.png", "walk_04.png"],
    fps: 12
)

animComp.animations["run"] = new Animation(
    frames: ["run_01.png", "run_02.png", "run_03.png"],
    fps: 20
)

animComp.animations["jump"] = new Animation(
    frames: ["jump_01.png", "jump_02.png"],
    fps: 10
)

// Later, retrieve and play an animation:
animComp.currentAnimation = "walk"
walkAnimation = animComp.animations["walk"]  // Gets the walk Animation object
currentFrame = walkAnimation.frames[animComp.currentFrame]  // Gets "walk_01.png"

// In JavaScript, this would be:
// animations = {
//     "walk": { frames: [...], fps: 12 },
//     "run": { frames: [...], fps: 20 }
// }
// walkAnim = animations["walk"]



// EXAMPLE 2: Component Storage in World


class World:
    // Store ALL components of ALL entities
    // Outer map: ComponentType -> Inner map
    // Inner map: EntityID -> Actual component
    map<ComponentType, map<EntityID, Component>> components

// What this means:
// components = {
//     PositionComponent: {
//         1: PositionComponent(x:0, y:0),
//         2: PositionComponent(x:10, y:5),
//         5: PositionComponent(x:-3, y:8)
//     },
//     VelocityComponent: {
//         1: VelocityComponent(x:1, y:0),
//         2: VelocityComponent(x:0, y:-2)
//     },
//     HealthComponent: {
//         2: HealthComponent(current:100, max:100)
//     }
// }

// How to use it:
world = new World()

// Get position of entity 1
positionMap = world.components[PositionComponent]  // Gets inner map
position = positionMap[1]                          // Gets PositionComponent(x:0, y:0)

// More concisely:
position = world.components[PositionComponent][1]

// Add component to entity 5
world.components[HealthComponent][5] = new HealthComponent(50, 100)



// EXAMPLE 3: Entity Tracking


class World:
    // Track which components each entity has
    map<EntityID, set<ComponentType>> entityComponents

// What this means:
// entityComponents = {
//     1: {PositionComponent, VelocityComponent, SpriteComponent},
//     2: {PositionComponent, VelocityComponent, HealthComponent},
//     3: {PositionComponent, AIComponent}
// }

// How to use it:
// Check if entity 1 has a VelocityComponent
if VelocityComponent in world.entityComponents[1]:
    print("Entity 1 can move!")

// Get all component types for entity 2
componentTypes = world.entityComponents[2]
// componentTypes = {PositionComponent, VelocityComponent, HealthComponent}

for componentType in componentTypes:
    print("Entity 2 has: " + componentType)



// EXAMPLE 4: Pooling System


class PoolingSystem:
    // Pool name -> Queue of available entities
    map<string, queue<EntityID>> pools

// What this means:
// pools = {
//     "bullet": queue([15, 16, 17, 18, 19]),  // Available bullet entities
//     "particle": queue([20, 21, 22, ...]),    // Available particle entities
//     "enemy": queue([30, 31])                 // Available enemy entities
// }

// How to use it:
pooling = new PoolingSystem()

// Get a bullet from the pool
if not pooling.pools["bullet"].isEmpty():
    bulletEntity = pooling.pools["bullet"].dequeue()  // Gets entity 15
    // Reuse entity 15 as a bullet
else:
    // Pool empty, create new bullet
    bulletEntity = createNewBullet()

// Return bullet to pool when done
pooling.pools["bullet"].enqueue(bulletEntity)  // Put it back for reuse



// EXAMPLE 5: Query Results


function query(required, excluded):
    // Returns list of entity IDs that match criteria
    list<EntityID> results = []
    
    // Check each entity
    for entity in allEntities:
        if hasAllComponents(entity, required) and hasNoneOf(entity, excluded):
            results.add(entity)
    
    return results

// Usage:
// Find all entities with Position AND Velocity but NOT Health
movingEntities = world.query(
    required: [PositionComponent, VelocityComponent],
    excluded: [HealthComponent]
)
// movingEntities might be: [1, 5, 7, 12]

// Then process them:
for entityId in movingEntities:
    position = world.getComponent(entityId, PositionComponent)
    velocity = world.getComponent(entityId, VelocityComponent)
    // Do something with position and velocity



// EXAMPLE 6: Event Queue


class World:
    queue<Event> eventQueue

// What this means:
// Events are processed in order (FIFO)
// eventQueue = [CollisionEvent, DamageEvent, EntityDiedEvent, ...]

// Adding events:
world.eventQueue.enqueue(new CollisionEvent(entity1, entity2))
world.eventQueue.enqueue(new DamageEvent(entity5, 25))

// Processing events:
while not world.eventQueue.isEmpty():
    event = world.eventQueue.dequeue()  // Get oldest event
    
    if event is CollisionEvent:
        handleCollision(event.entity1, event.entity2)
    else if event is DamageEvent:
        applyDamage(event.target, event.amount)
```

##### Type Notation Explained

```pseudo

// GENERIC TYPE PARAMETERS


// Syntax: Type<ParameterType>
// This means "a Type that holds ParameterType"

array<int>              // Array that holds integers
array<string>           // Array that holds strings
array<Entity>           // Array that holds Entity objects

map<string, int>        // Map with string keys and integer values
map<int, Player>        // Map with integer keys and Player values

queue<Event>            // Queue that holds Event objects
set<EntityID>           // Set that holds EntityID values

// Multiple parameters:
map<KeyType, ValueType>         // Two type parameters
map<string, array<int>>         // Value can be complex type
map<EntityID, map<string, int>> // Nested maps



// COMPARISON: DIFFERENT LANGUAGES


// This pseudo-code:
map<string, Animation> animations

// Equivalent in various languages:

// C++:
std::map<std::string, Animation> animations;
std::unordered_map<std::string, Animation> animations; // Faster

// JavaScript:
const animations = {};  // Object
const animations = new Map();  // ES6 Map

// Python:
animations = {}  ### Dictionary

// C#:
Dictionary<string, Animation> animations;

// Java:
HashMap<String, Animation> animations;

// Rust:
use std::collections::HashMap;
let mut animations: HashMap<String, Animation> = HashMap::new();
```

##### Common Patterns Explained

```pseudo

// PATTERN 1: Nested Maps (2D Storage)


map<ComponentType, map<EntityID, Component>> components

// This is a map of maps - think of it as a 2D table:
//
//                    Entity 1    Entity 2    Entity 3
// PositionComponent:  Pos(0,0)    Pos(5,5)    Pos(2,3)
// VelocityComponent:  Vel(1,0)    Vel(0,1)    ---
// HealthComponent:    ---         Health(100) Health(50)
//
// Access: components[PositionComponent][1] gives you Pos(0,0)



// PATTERN 2: Checking Membership


// Check if key exists in map
if "keyName" in myMap:
    // Key exists

if myMap.contains("keyName"):  // Alternative syntax
    // Key exists

// Check if item exists in set
if entity in entitySet:
    // Entity is in set

// Check if item exists in array
if myArray.contains(item):
    // Item is in array



// PATTERN 3: Iteration Patterns


// Iterate over array/list
for item in myArray:
    process(item)

// Iterate over map (get both key and value)
for key, value in myMap:
    print(key + " -> " + value)

// Iterate over map (just keys)
for key in myMap.keys():
    value = myMap[key]

// Iterate with index
for i in 0 to array.length:
    item = array[i]
    print("Index " + i + ": " + item)



// PATTERN 4: Null/None Checking


// Check if something exists before using it
component = world.getComponent(entity, PositionComponent)

if component != null:
    // Safe to use component
    print(component.x)
else:
    // Component doesn't exist
    print("Entity has no position")

// Alternative syntax
if component:
    // Truthy check (component exists)

if not component:
    // Component doesn't exist
```

---

#### Introduction


##### What is ECS?

Entity-Component-System is an architectural pattern that prioritizes
*composition over inheritance* and *data-oriented design* over
object-oriented design.

*Key Philosophy:*
- Entities are just IDs (pure identity)
- Components are just data (no behavior)
- Systems are just logic (no data)


##### Why ECS for Large Games?

| Traditional OOP | ECS |
|----------------|-----|
| Rigid inheritance trees | Flexible composition |
| Scattered memory layout | Cache-friendly arrays |
| Tight coupling | Loose coupling |
| Hard to parallelize | Easy to parallelize |
| Code duplication | Reusable components |



#### Core Concepts

##### 1. Entity
An entity is simply a unique identifier. Think of it as a "container" or
"tag" that groups components together.

```
Entity = Unique ID (integer)
Examples: 1, 2, 3, 42, 1337...
```

##### 2. Component
Pure data structures with no logic. They describe *what* an entity is.

```
Component = Struct/Class with only data fields
NO methods (except constructors/getters/setters)
```

##### 3. System
Pure logic that operates on entities with specific component combinations.
They describe *how* things behave.

```
System = Function that queries components and performs logic
NO state (except caching for optimization)
```

##### 4. World
The container that manages all entities, components, and systems.

```
World = Central registry + Query engine + System orchestrator
```



#### Complete Pseudo-code Implementation

##### Core Architecture

```pseudo

// COMPONENT DEFINITIONS (Pure Data)

class PositionComponent:
    float x
    float y
    float z

class VelocityComponent:
    float x
    float y
    float z

class HealthComponent:
    int current
    int max
    
class SpriteComponent:
    string texture
    int width
    int height
    int layer  // Render order

class InputComponent:
    // Tag component - presence indicates player control
    pass

class AIComponent:
    enum State { IDLE, PATROL, CHASE, ATTACK, FLEE }
    State currentState
    EntityID targetId
    float detectionRadius
    
class ColliderComponent:
    enum Shape { CIRCLE, BOX, POLYGON }
    Shape shape
    float radius  // For circle
    float width, height  // For box
    bool isTrigger  // Doesn't physically collide

class RigidBodyComponent:
    float mass
    float drag
    bool isStatic
    
class DamageComponent:
    int amount
    EntityID source  // Who caused the damage
    
class LifespanComponent:
    float remaining
    float initial
    
class AnimationComponent:
    string currentAnimation
    float frameTime
    int currentFrame
    map<string, Animation> animations

class ParticleEmitterComponent:
    int particlesPerSecond
    float lifetime
    Vector3 direction
    float spread

class AudioComponent:
    string soundId
    bool isLooping
    float volume

class InventoryComponent:
    list<EntityID> items
    int maxSlots

class TransformComponent:
    Vector3 position
    Vector3 rotation
    Vector3 scale
    EntityID parent  // For hierarchy

class TagComponent:
    set<string> tags  // e.g., "enemy", "projectile", "collectible"



// WORLD (Component Manager)

class World:
    // Core data structures
    int nextEntityId = 1
    set<EntityID> entities
    
    // Component storage: ComponentType -> (EntityID -> Component)
    map<ComponentType, map<EntityID, Component>> components
    
    // Optimization: Track which entities have which components
    map<ComponentType, set<EntityID>> componentIndex
    
    // Entity metadata
    map<EntityID, set<ComponentType>> entityComponents
    
    // Systems registry
    list<System> systems
    
    // Event queue
    queue<Event> eventQueue
    
    
    // Entity Management
    
    function createEntity() -> EntityID:
        id = nextEntityId++
        entities.add(id)
        entityComponents[id] = empty set
        return id
    
    function destroyEntity(EntityID id):
        if not entities.contains(id):
            return
        
        // Remove all components
        for componentType in entityComponents[id]:
            removeComponent(id, componentType)
        
        entityComponents.remove(id)
        entities.remove(id)
        
        // Emit event
        emitEvent(EntityDestroyedEvent(id))
    
    function isEntityAlive(EntityID id) -> bool:
        return entities.contains(id)
    
    
    // Component Management
        
    function addComponent(EntityID id, Component component):
        componentType = component.getType()
        
        // Store component
        if componentType not in components:
            components[componentType] = empty map
            componentIndex[componentType] = empty set
        
        components[componentType][id] = component
        componentIndex[componentType].add(id)
        entityComponents[id].add(componentType)
        
        // Emit event
        emitEvent(ComponentAddedEvent(id, componentType))
    
    function removeComponent(EntityID id, ComponentType type):
        if type in components and id in components[type]:
            components[type].remove(id)
            componentIndex[type].remove(id)
            entityComponents[id].remove(type)
            
            emitEvent(ComponentRemovedEvent(id, type))
    
    function getComponent(EntityID id, ComponentType type) -> Component:
        if type in components and id in components[type]:
            return components[type][id]
        return null
    
    function hasComponent(EntityID id, ComponentType type) -> bool:
        return type in entityComponents[id]
    
    function hasComponents(EntityID id, list<ComponentType> types) -> bool:
        for type in types:
            if not hasComponent(id, type):
                return false
        return true
    
    
    // Query System (The Heart of ECS)
    
    function query(list<ComponentType> required, 
                   list<ComponentType> excluded = []) -> list<EntityID>:
        
        if required.isEmpty():
            return []
        
        // Start with smallest set for optimization
        smallestSet = componentIndex[required[0]]
        for type in required[1:]:
            if componentIndex[type].size() < smallestSet.size():
                smallestSet = componentIndex[type]
        
        result = []
        for entityId in smallestSet:
            // Check all required components
            hasAll = true
            for type in required:
                if not hasComponent(entityId, type):
                    hasAll = false
                    break
            
            if not hasAll:
                continue
            
            // Check excluded components
            hasExcluded = false
            for type in excluded:
                if hasComponent(entityId, type):
                    hasExcluded = true
                    break
            
            if not hasExcluded:
                result.add(entityId)
        
        return result
    
    
    // System Management
    
    function addSystem(System system):
        systems.add(system)
        system.initialize(this)
    
    function update(float deltaTime):
        // Update all systems in order
        for system in systems:
            system.update(this, deltaTime)
        
        // Process events
        processEvents()
    
    
    // Event System
    
    function emitEvent(Event event):
        eventQueue.enqueue(event)
    
    function processEvents():
        while not eventQueue.isEmpty():
            event = eventQueue.dequeue()
            
            for system in systems:
                system.onEvent(this, event)



// SYSTEM DEFINITIONS (Pure Logic)

// Base system class
abstract class System:
    abstract function update(World world, float dt)
    
    function initialize(World world):
        pass
    
    function onEvent(World world, Event event):
        pass


// Input System

class InputSystem extends System:
    InputState currentInput
    
    function update(World world, float dt):
        currentInput = pollInput()
        
        // Query all entities with Input + Velocity components
        entities = world.query([InputComponent, VelocityComponent])
        
        for entityId in entities:
            velocity = world.getComponent(entityId, VelocityComponent)
            
            // Process input
            velocity.x = 0
            velocity.y = 0
            
            if currentInput.left:
                velocity.x = -5.0
            if currentInput.right:
                velocity.x = 5.0
            if currentInput.up:
                velocity.y = -5.0
            if currentInput.down:
                velocity.y = 5.0
            
            // Shoot on space
            if currentInput.spacePressed:
                world.emitEvent(ShootEvent(entityId))


// Movement System

class MovementSystem extends System:
    function update(World world, float dt):
        entities = world.query([PositionComponent, VelocityComponent])
        
        for entityId in entities:
            position = world.getComponent(entityId, PositionComponent)
            velocity = world.getComponent(entityId, VelocityComponent)
            
            // Apply velocity
            position.x += velocity.x * dt
            position.y += velocity.y * dt
            position.z += velocity.z * dt


// Physics System

class PhysicsSystem extends System:
    Vector3 gravity = (0, 9.8, 0)
    
    function update(World world, float dt):
        entities = world.query([VelocityComponent, RigidBodyComponent])
        
        for entityId in entities:
            velocity = world.getComponent(entityId, VelocityComponent)
            rigidBody = world.getComponent(entityId, RigidBodyComponent)
            
            if not rigidBody.isStatic:
                // Apply gravity
                velocity.y += gravity.y * rigidBody.mass * dt
                
                // Apply drag
                velocity.x *= (1.0 - rigidBody.drag * dt)
                velocity.y *= (1.0 - rigidBody.drag * dt)
                velocity.z *= (1.0 - rigidBody.drag * dt)


// Collision System

class CollisionSystem extends System:
    function update(World world, float dt):
        entities = world.query([PositionComponent, ColliderComponent])
        
        // Broad phase: Check all pairs
        for i in 0 to entities.length:
            for j in i+1 to entities.length:
                entity1 = entities[i]
                entity2 = entities[j]
                
                pos1 = world.getComponent(entity1, PositionComponent)
                pos2 = world.getComponent(entity2, PositionComponent)
                col1 = world.getComponent(entity1, ColliderComponent)
                col2 = world.getComponent(entity2, ColliderComponent)
                
                // Narrow phase: Detailed collision check
                if checkCollision(pos1, col1, pos2, col2):
                    world.emitEvent(CollisionEvent(entity1, entity2))
                    
                    // Physical response (if not trigger)
                    if not col1.isTrigger and not col2.isTrigger:
                        resolveCollision(world, entity1, entity2)
    
    function checkCollision(pos1, col1, pos2, col2) -> bool:
        if col1.shape == CIRCLE and col2.shape == CIRCLE:
            distance = sqrt((pos1.x - pos2.x)^2 + (pos1.y - pos2.y)^2)
            return distance < (col1.radius + col2.radius)
        
        // Add more collision checks for other shapes
        return false
    
    function resolveCollision(World world, entity1, entity2):
        // Push entities apart, apply bounce, etc.
        pass


// Health System

class HealthSystem extends System:
    function update(World world, float dt):
        entities = world.query([HealthComponent])
        
        for entityId in entities:
            health = world.getComponent(entityId, HealthComponent)
            
            // Check for death
            if health.current <= 0:
                world.emitEvent(EntityDiedEvent(entityId))
                world.destroyEntity(entityId)
    
    function onEvent(World world, Event event):
        if event is CollisionEvent:
            entity1 = event.entity1
            entity2 = event.entity2
            
            // Check if entity1 has damage and entity2 has health
            if world.hasComponent(entity1, DamageComponent):
                damage = world.getComponent(entity1, DamageComponent)
                
                if world.hasComponent(entity2, HealthComponent):
                    health = world.getComponent(entity2, HealthComponent)
                    health.current -= damage.amount
                    
                    world.emitEvent(DamageDealtEvent(entity2, damage.amount))


// AI System

class AISystem extends System:
    function update(World world, float dt):
        entities = world.query([AIComponent, PositionComponent, VelocityComponent])
        
        for entityId in entities:
            ai = world.getComponent(entityId, AIComponent)
            position = world.getComponent(entityId, PositionComponent)
            velocity = world.getComponent(entityId, VelocityComponent)
            
            // State machine
            switch ai.currentState:
                case IDLE:
                    updateIdle(world, entityId, ai, position, velocity, dt)
                case PATROL:
                    updatePatrol(world, entityId, ai, position, velocity, dt)
                case CHASE:
                    updateChase(world, entityId, ai, position, velocity, dt)
                case ATTACK:
                    updateAttack(world, entityId, ai, position, velocity, dt)
                case FLEE:
                    updateFlee(world, entityId, ai, position, velocity, dt)
    
    function updateChase(world, entityId, ai, position, velocity, dt):
        // Find player
        players = world.query([InputComponent, PositionComponent])
        
        if players.isEmpty():
            ai.currentState = IDLE
            return
        
        targetPos = world.getComponent(players[0], PositionComponent)
        
        // Move towards player
        direction = normalize(targetPos - position)
        velocity.x = direction.x * 3.0
        velocity.y = direction.y * 3.0
        
        // Check if in attack range
        distance = length(targetPos - position)
        if distance < 2.0:
            ai.currentState = ATTACK


// Lifespan System

class LifespanSystem extends System:
    function update(World world, float dt):
        entities = world.query([LifespanComponent])
        
        for entityId in entities:
            lifespan = world.getComponent(entityId, LifespanComponent)
            
            lifespan.remaining -= dt
            
            if lifespan.remaining <= 0:
                world.destroyEntity(entityId)


// Animation System

class AnimationSystem extends System:
    function update(World world, float dt):
        entities = world.query([AnimationComponent, SpriteComponent])
        
        for entityId in entities:
            animation = world.getComponent(entityId, AnimationComponent)
            sprite = world.getComponent(entityId, SpriteComponent)
            
            // Update frame time
            animation.frameTime += dt
            
            currentAnim = animation.animations[animation.currentAnimation]
            frameDuration = 1.0 / currentAnim.fps
            
            if animation.frameTime >= frameDuration:
                animation.frameTime = 0
                animation.currentFrame++
                
                if animation.currentFrame >= currentAnim.frameCount:
                    animation.currentFrame = 0
            
            // Update sprite texture
            sprite.texture = currentAnim.getFrame(animation.currentFrame)


// Render System

class RenderSystem extends System:
    Renderer renderer
    
    function initialize(World world):
        renderer = new Renderer()
    
    function update(World world, float dt):
        renderer.clear()
        
        // Query all visible entities
        entities = world.query([PositionComponent, SpriteComponent])
        
        // Sort by layer for correct rendering order
        sortedEntities = sortByLayer(entities, world)
        
        for entityId in sortedEntities:
            position = world.getComponent(entityId, PositionComponent)
            sprite = world.getComponent(entityId, SpriteComponent)
            
            renderer.draw(sprite.texture, position.x, position.y)
        
        renderer.present()



// GAME CLASS (Orchestration)

class Game:
    World world
    bool running
    float targetFPS = 60.0
    
    function initialize():
        world = new World()
        
        // Register systems (ORDER MATTERS!)
        world.addSystem(new InputSystem())
        world.addSystem(new AISystem())
        world.addSystem(new PhysicsSystem())
        world.addSystem(new MovementSystem())
        world.addSystem(new CollisionSystem())
        world.addSystem(new HealthSystem())
        world.addSystem(new LifespanSystem())
        world.addSystem(new AnimationSystem())
        world.addSystem(new RenderSystem())
        
        // Create initial entities
        createPlayer()
        createEnemies()
        createWorld()
    
    function createPlayer() -> EntityID:
        player = world.createEntity()
        
        world.addComponent(player, PositionComponent(0, 0, 0))
        world.addComponent(player, VelocityComponent(0, 0, 0))
        world.addComponent(player, HealthComponent(100, 100))
        world.addComponent(player, InputComponent())
        world.addComponent(player, SpriteComponent("player.png", 32, 32, 10))
        world.addComponent(player, ColliderComponent(CIRCLE, 16))
        world.addComponent(player, RigidBodyComponent(1.0, 0.1, false))
        
        return player
    
    function createEnemy(float x, float y) -> EntityID:
        enemy = world.createEntity()
        
        world.addComponent(enemy, PositionComponent(x, y, 0))
        world.addComponent(enemy, VelocityComponent(0, 0, 0))
        world.addComponent(enemy, HealthComponent(50, 50))
        world.addComponent(enemy, AIComponent(PATROL, null, 10.0))
        world.addComponent(enemy, SpriteComponent("enemy.png", 32, 32, 5))
        world.addComponent(enemy, ColliderComponent(CIRCLE, 16))
        world.addComponent(enemy, RigidBodyComponent(1.0, 0.1, false))
        
        return enemy
    
    function createBullet(float x, float y, float dirX, float dirY, EntityID source):
        bullet = world.createEntity()
        
        world.addComponent(bullet, PositionComponent(x, y, 0))
        world.addComponent(bullet, VelocityComponent(dirX * 10, dirY * 10, 0))
        world.addComponent(bullet, SpriteComponent("bullet.png", 8, 8, 8))
        world.addComponent(bullet, ColliderComponent(CIRCLE, 4, true))
        world.addComponent(bullet, DamageComponent(25, source))
        world.addComponent(bullet, LifespanComponent(3.0, 3.0))
        
        return bullet
    
    function run():
        running = true
        lastTime = getCurrentTime()
        
        while running:
            currentTime = getCurrentTime()
            deltaTime = currentTime - lastTime
            lastTime = currentTime
            
            // Fixed timestep for physics
            world.update(deltaTime)
            
            // Frame rate limiting
            sleep(1.0 / targetFPS - deltaTime)
    
    function shutdown():
        running = false



// USAGE EXAMPLE

function main():
    game = new Game()
    game.initialize()
    game.run()
    game.shutdown()
```



#### Advanced Patterns

##### 1. Component Groups (Archetypes)

For optimization, group entities by their component signature:

```pseudo
class World:
    map<ArchetypeID, list<EntityID>> archetypes
    map<EntityID, ArchetypeID> entityArchetype
    
    function getArchetypeID(set<ComponentType> components) -> ArchetypeID:
        // Hash the component set
        return hash(sort(components))
    
    function query(required, excluded):
        results = []
        
        for archetypeID, entities in archetypes:
            archetype = getArchetypeComponents(archetypeID)
            
            if archetype.containsAll(required) and not archetype.containsAny(excluded):
                results.addAll(entities)
        
        return results
```

##### 2. Sparse Set Component Storage

Extremely fast iteration and lookup:

```pseudo
class SparseSet:
    array<int> sparse  // EntityID -> Index in dense
    array<EntityID> dense  // Actual entity IDs
    array<Component> components  // Component data
    int size
    
    function add(EntityID entity, Component component):
        sparse[entity] = size
        dense[size] = entity
        components[size] = component
        size++
    
    function remove(EntityID entity):
        index = sparse[entity]
        lastEntity = dense[size - 1]
        
        // Swap with last element
        dense[index] = lastEntity
        components[index] = components[size - 1]
        sparse[lastEntity] = index
        
        size--
    
    function get(EntityID entity) -> Component:
        return components[sparse[entity]]
```

##### 3. System Dependencies

Declare what systems depend on:

```pseudo
class System:
    list<SystemType> dependencies
    
    function getDependencies() -> list<SystemType>:
        return dependencies

class World:
    function sortSystems():
        // Topological sort based on dependencies
        sorted = topologicalSort(systems)
        systems = sorted
```

##### 4. Deferred Component Changes

Avoid modifying components during iteration:

```pseudo
class World:
    queue<ComponentOperation> deferredOperations
    
    function deferredAddComponent(entity, component):
        deferredOperations.enqueue(AddOp(entity, component))
    
    function processDeferredOperations():
        while not deferredOperations.isEmpty():
            op = deferredOperations.dequeue()
            op.execute(this)
```


#### Extension Roadmap

##### Phase 1: Core Features
- [x] Basic ECS structure
- [x] Component storage
- [x] Query system
- [x] Basic systems (input, movement, render)

##### Phase 2: Gameplay Systems
```pseudo
class WeaponSystem extends System
class InventorySystem extends System
class DialogueSystem extends System
class QuestSystem extends System
class SaveLoadSystem extends System
```

##### Phase 3: Performance
```pseudo
class SpatialHashGrid:
    // Fast collision detection
    map<GridCell, list<EntityID>> grid
    
class ObjectPoolSystem:
    // Reuse entities instead of creating/destroying
    map<string, queue<EntityID>> pools

class ParallelSystemExecutor:
    // Run independent systems on multiple threads
    function executeParallel(systems)
```

##### Phase 4: Advanced Features
```pseudo
class NetworkReplicationSystem:
    // Sync entities across network
    function replicateEntity(EntityID)
    
class PrefabSystem:
    // Template-based entity creation
    map<string, EntityTemplate> prefabs
    
class ScriptingSystem:
    // Lua/Python integration for modding
    ScriptEngine engine
```

##### Phase 5: Editor Tools
```pseudo
class EntityInspector:
    // Debug and edit entities at runtime
    function inspectEntity(EntityID)
    function editComponent(EntityID, ComponentType)

class WorldSerializer:
    // Save/load entire world state
    function serialize() -> bytes
    function deserialize(bytes)
```



#### Performance Optimization

##### Memory Layout

```pseudo
// Bad: Array of Structs (AoS)
struct Entity {
    Position pos
    Velocity vel
    Health hp
    Sprite sprite
}
array<Entity> entities  // Scattered memory access

// Good: Struct of Arrays (SoA)
struct World {
    array<Position> positions
    array<Velocity> velocities
    array<Health> healths
    array<Sprite> sprites
}
// Cache-friendly sequential access
```

##### Batch Processing

```pseudo
class RenderSystem:
    function update(world, dt):
        // Group by texture for batch rendering
        batches = groupByTexture(world.query([Sprite, Position]))
        
        for texture, entities in batches:
            renderer.bindTexture(texture)
            
            for entity in entities:
                // Draw all entities with same texture
                renderer.drawBatched(entity)
```

##### Dirty Flags

```pseudo
class TransformComponent:
    Vector3 position
    Matrix4x4 matrix
    bool isDirty
    
class TransformSystem:
    function update(world, dt):
        entities = world.query([TransformComponent])
        
        for entity in entities:
            transform = world.getComponent(entity, TransformComponent)
            
            if transform.isDirty:
                transform.matrix = calculateMatrix(transform.position)
                transform.isDirty = false
```



#### Real-World Examples

##### Example 1: RPG Character

```pseudo
function createRPGCharacter(name, class):
    character = world.createEntity()
    
    // Core components
    world.addComponent(character, PositionComponent(0, 0, 0))
    world.addComponent(character, VelocityComponent(0, 0, 0))
    world.addComponent(character, SpriteComponent(class + ".png"))
    
    // RPG components
    world.addComponent(character, StatsComponent(
        level: 1,
        experience: 0,
        strength: 10,
        dexterity: 10,
        intelligence: 10
    ))
    
    world.addComponent(character, InventoryComponent(
        maxSlots: 20,
        gold: 0
    ))
    
    world.addComponent(character, EquipmentComponent(
        weapon: null,
        armor: null,
        accessory: null
    ))
    
    world.addComponent(character, SkillsComponent(
        skills: ["Basic Attack", "Heal"]
    ))
    
    return character
```

##### Example 2: Tower Defense Enemy

```pseudo
function createTDEnemy(path):
    enemy = world.createEntity()
    
    world.addComponent(enemy, PositionComponent(path.start))
    world.addComponent(enemy, PathFollowingComponent(
        path: path,
        speed: 2.0,
        progress: 0.0
    ))
    
    world.addComponent(enemy, HealthComponent(100, 100))
    world.addComponent(enemy, SpriteComponent("enemy.png"))
    world.addComponent(enemy, ColliderComponent(CIRCLE, 16))
    
    world.addComponent(enemy, RewardComponent(
        gold: 50,
        experience: 10
    ))
    
    world.addComponent(enemy, TagComponent(["enemy", "ground"]))
    
    return enemy
```

##### Example 3: Particle System

```pseudo
function createParticleSystem(x, y):
    emitter = world.createEntity()
    
    world.addComponent(emitter, PositionComponent(x, y, 0))
    world.addComponent(emitter, ParticleEmitterComponent(
        particlesPerSecond: 100,
        lifetime: 2.0,
        direction: Vector3(0, -1, 0),
        spread: 45.0
    ))
    
    return emitter

class ParticleSystem extends System:
    function update(world, dt):
        emitters = world.query([ParticleEmitterComponent, PositionComponent])
        
        for emitterId in emitters:
            emitter = world.getComponent(emitterId, ParticleEmitterComponent)
            position = world.getComponent(emitterId, PositionComponent)
            
            // Spawn particles
            toSpawn = emitter.particlesPerSecond * dt
            
            for i in 0 to toSpawn:
                particle = world.createEntity()
                
                // Randomize direction within spread
                angle = random(-emitter.spread, emitter.spread)
                direction = rotate(emitter.direction, angle)
                
                world.addComponent(particle, PositionComponent(position.x, position.y, 0))
                world.addComponent(particle, VelocityComponent(direction.x * 5, direction.y * 5, 0))
                world.addComponent(particle, SpriteComponent("particle.png"))
                world.addComponent(particle, LifespanComponent(emitter.lifetime))
                world.addComponent(particle, FadeComponent(1.0, 0.0, emitter.lifetime))
```



#### Best Practices

##### 1. Keep Components Small
```pseudo
// Bad: God component
class CharacterComponent:
    position, velocity, health, mana, inventory, skills, quests...

// Good: Focused components
class PositionComponent: x, y, z
class HealthComponent: current, max
class ManaComponent: current, max
```

##### 2. Systems Should Be Stateless
```pseudo
// Bad: Stateful system
class AISystem:
    map<EntityID, AIState> states  // Don't store state in system

// Good: State in components
class AIComponent:
    AIState state  // State belongs in component
```

##### 3. Use Events for Cross-System Communication
```pseudo
// Instead of systems calling each other
class CombatSystem:
    function dealDamage(entity, amount):
        world.emitEvent(DamageEvent(entity, amount))
        // HealthSystem will handle this event
```

##### 4. Design for Cache Coherency
```pseudo
// Process components in contiguous memory
for i in 0 to positions.length:
    position = positions[i]
    velocity = velocities[i]
    // Fast sequential access
```



#### Common Patterns and Recipes

##### Pattern 1: Pooling System

```pseudo
class PoolingSystem extends System:
    map<string, queue<EntityID>> pools
    map<EntityID, string> entityPool
    
    function getPooledEntity(poolName, createFunction) -> EntityID:
        if pools[poolName].isEmpty():
            entity = createFunction()
            entityPool[entity] = poolName
            return entity
        else:
            entity = pools[poolName].dequeue()
            reactivateEntity(world, entity)
            return entity
    
    function returnToPool(EntityID entity):
        poolName = entityPool[entity]
        deactivateEntity(world, entity)
        pools[poolName].enqueue(entity)
    
    function deactivateEntity(World world, EntityID entity):
        // Instead of destroying, disable rendering and logic
        world.removeComponent(entity, SpriteComponent)
        world.addComponent(entity, DisabledComponent())
    
    function reactivateEntity(World world, EntityID entity):
        world.removeComponent(entity, DisabledComponent)

// Usage:
bullet = poolingSystem.getPooledEntity("bullet", () => createBullet())
// When done: poolingSystem.returnToPool(bullet)
```

##### Pattern 2: State Machine Component

```pseudo
class StateMachineComponent:
    enum StateID
    StateID currentState
    map<StateID, State> states
    float timeInState
    
class State:
    function onEnter(World world, EntityID entity)
    function onUpdate(World world, EntityID entity, float dt)
    function onExit(World world, EntityID entity)
    function checkTransitions() -> StateID

class StateMachineSystem extends System:
    function update(World world, float dt):
        entities = world.query([StateMachineComponent])
        
        for entityId in entities:
            sm = world.getComponent(entityId, StateMachineComponent)
            
            currentState = sm.states[sm.currentState]
            
            // Check for state transitions
            newStateId = currentState.checkTransitions()
            
            if newStateId != sm.currentState:
                currentState.onExit(world, entityId)
                sm.currentState = newStateId
                sm.timeInState = 0
                sm.states[newStateId].onEnter(world, entityId)
            else:
                currentState.onUpdate(world, entityId, dt)
                sm.timeInState += dt

// Example: Enemy AI States
class IdleState extends State:
    function checkTransitions() -> StateID:
        if playerInRange():
            return StateID.CHASE
        return StateID.IDLE

class ChaseState extends State:
    function onUpdate(world, entity, dt):
        moveTowardsPlayer(world, entity)
    
    function checkTransitions() -> StateID:
        if playerTooFar():
            return StateID.IDLE
        if playerInAttackRange():
            return StateID.ATTACK
        return StateID.CHASE
```

##### Pattern 3: Hierarchical Transforms

```pseudo
class TransformComponent:
    Vector3 localPosition
    Vector3 localRotation
    Vector3 localScale
    
    Matrix4x4 worldMatrix
    bool isDirty
    
    EntityID parent
    list<EntityID> children

class TransformSystem extends System:
    function update(World world, float dt):
        // Process root entities first
        roots = world.query([TransformComponent], excluding: [ChildComponent])
        
        for rootId in roots:
            updateTransformHierarchy(world, rootId, Matrix4x4.identity())
    
    function updateTransformHierarchy(world, entity, parentMatrix):
        transform = world.getComponent(entity, TransformComponent)
        
        if transform.isDirty or parentMatrix != previousParentMatrix:
            // Calculate local matrix
            localMatrix = createMatrix(
                transform.localPosition,
                transform.localRotation,
                transform.localScale
            )
            
            // Combine with parent
            transform.worldMatrix = parentMatrix * localMatrix
            transform.isDirty = false
        
        // Recursively update children
        for child in transform.children:
            updateTransformHierarchy(world, child, transform.worldMatrix)

// Usage: Weapon attached to player
player = createPlayer()
weapon = world.createEntity()
world.addComponent(weapon, TransformComponent(
    localPosition: (1, 0, 0),  // Offset from player
    parent: player
))

playerTransform = world.getComponent(player, TransformComponent)
playerTransform.children.add(weapon)
```

##### Pattern 4: Component Dependencies

```pseudo
class ComponentDependency:
    ComponentType dependent
    list<ComponentType> requires
    
    function validate(World world, EntityID entity) -> bool:
        for required in requires:
            if not world.hasComponent(entity, required):
                return false
        return true

class World:
    list<ComponentDependency> dependencies
    
    function registerDependency(dependent, requires):
        dependencies.add(ComponentDependency(dependent, requires))
    
    function addComponent(entity, component):
        componentType = component.getType()
        
        // Check dependencies
        for dep in dependencies:
            if dep.dependent == componentType:
                if not dep.validate(this, entity):
                    error("Missing dependencies: " + dep.requires)
        
        // Add component...

// Example: Sprite requires Position
world.registerDependency(SpriteComponent, [PositionComponent])
world.registerDependency(VelocityComponent, [PositionComponent])
world.registerDependency(ColliderComponent, [PositionComponent])
```

##### Pattern 5: Query Caching

```pseudo
class World:
    map<QuerySignature, CachedQuery> queryCache
    
    class CachedQuery:
        list<EntityID> results
        int version
        
    int worldVersion = 0
    
    function addComponent(entity, component):
        // ... add component logic ...
        worldVersion++  // Invalidate caches
    
    function removeComponent(entity, type):
        // ... remove component logic ...
        worldVersion++
    
    function query(required, excluded) -> list<EntityID>:
        signature = QuerySignature(required, excluded)
        
        if signature in queryCache:
            cached = queryCache[signature]
            
            if cached.version == worldVersion:
                return cached.results  // Return cached results
        
        // Compute query
        results = computeQuery(required, excluded)
        
        // Cache it
        queryCache[signature] = CachedQuery(results, worldVersion)
        
        return results
```

##### Pattern 6: Tag Components

```pseudo
// Tag components have no data - just presence
class PlayerTag:
    pass

class EnemyTag:
    pass

class ProjectileTag:
    pass

class BossTag:
    pass

// Usage: Fast filtering
players = world.query([PlayerTag])
enemies = world.query([EnemyTag])
enemyBosses = world.query([EnemyTag, BossTag])

// More flexible than enums or type IDs
// Can combine multiple tags per entity
```

##### Pattern 7: Reactive Systems (Event-Driven)

```pseudo
class ReactiveSystem extends System:
    abstract function onComponentAdded(world, entity, component)
    abstract function onComponentRemoved(world, entity, type)
    
    function update(world, dt):
        pass  // No regular update needed
    
    function onEvent(world, event):
        if event is ComponentAddedEvent:
            if shouldReactTo(event.componentType):
                onComponentAdded(world, event.entity, event.component)
        
        if event is ComponentRemovedEvent:
            if shouldReactTo(event.componentType):
                onComponentRemoved(world, event.entity, event.componentType)

// Example: Auto-register colliders with physics engine
class ColliderRegistrationSystem extends ReactiveSystem:
    PhysicsEngine physicsEngine
    
    function onComponentAdded(world, entity, component):
        if component is ColliderComponent:
            position = world.getComponent(entity, PositionComponent)
            physicsEngine.registerCollider(entity, position, component)
    
    function onComponentRemoved(world, entity, type):
        if type is ColliderComponent:
            physicsEngine.unregisterCollider(entity)
```

##### Pattern 8: Blackboard/Shared Data

```pseudo
class Blackboard:
    map<string, any> data
    
    function set(key, value):
        data[key] = value
    
    function get(key):
        return data[key]
    
    function has(key) -> bool:
        return key in data

class World:
    Blackboard blackboard
    
// Usage: Share data between systems without coupling
class SpawnSystem:
    function update(world, dt):
        if world.blackboard.get("currentWave") == 5:
            spawnBoss()
            world.blackboard.set("bossActive", true)

class MusicSystem:
    function update(world, dt):
        if world.blackboard.get("bossActive"):
            playBossMusic()
```



#### Advanced System Examples

##### Spatial Partitioning System

```pseudo
class SpatialHashGrid:
    float cellSize
    map<GridCoord, list<EntityID>> grid
    
    function insert(EntityID entity, Vector3 position):
        coord = worldToGrid(position)
        grid[coord].add(entity)
    
    function query(Vector3 position, float radius) -> list<EntityID>:
        results = []
        
        // Check all cells in radius
        minCell = worldToGrid(position - radius)
        maxCell = worldToGrid(position + radius)
        
        for x in minCell.x to maxCell.x:
            for y in minCell.y to maxCell.y:
                coord = GridCoord(x, y)
                if coord in grid:
                    results.addAll(grid[coord])
        
        return results

class SpatialSystem extends System:
    SpatialHashGrid grid
    
    function update(World world, float dt):
        grid.clear()
        
        // Rebuild grid every frame
        entities = world.query([PositionComponent])
        
        for entity in entities:
            position = world.getComponent(entity, PositionComponent)
            grid.insert(entity, position)

class OptimizedCollisionSystem extends System:
    function update(World world, float dt):
        spatialSystem = world.getSystem(SpatialSystem)
        entities = world.query([PositionComponent, ColliderComponent])
        
        for entity in entities:
            position = world.getComponent(entity, PositionComponent)
            collider = world.getComponent(entity, ColliderComponent)
            
            // Only check nearby entities
            nearby = spatialSystem.grid.query(position, collider.radius * 2)
            
            for other in nearby:
                if other != entity:
                    checkCollision(world, entity, other)
```

##### Network Replication System

```pseudo
class NetworkComponent:
    bool isReplicated
    bool isAuthoritative  // Server-controlled
    int ownerId  // Which client owns this
    int lastReplicatedTick

class ReplicationSystem extends System:
    NetworkManager network
    int currentTick = 0
    
    function update(World world, float dt):
        currentTick++
        
        if network.isServer():
            replicateToClients(world)
        else:
            receiveReplication(world)
    
    function replicateToClients(World world):
        entities = world.query([NetworkComponent])
        
        packet = new ReplicationPacket()
        
        for entity in entities:
            netComp = world.getComponent(entity, NetworkComponent)
            
            if not netComp.isReplicated:
                continue
            
            // Check if needs update
            if entityChanged(entity) or currentTick - netComp.lastReplicatedTick > 10:
                packet.addEntity(entity, serializeEntity(world, entity))
                netComp.lastReplicatedTick = currentTick
        
        network.broadcast(packet)
    
    function receiveReplication(World world):
        while network.hasPacket():
            packet = network.receivePacket()
            
            for entityData in packet.entities:
                entity = findOrCreateEntity(entityData.id)
                deserializeEntity(world, entity, entityData)

class PredictionSystem extends System:
    // Client-side prediction for smooth gameplay
    function update(World world, float dt):
        if not network.isClient():
            return
        
        // Predict player movement locally
        localPlayer = getLocalPlayer()
        
        if localPlayer:
            // Store prediction
            recordPrediction(localPlayer)
            
            // Apply input immediately
            applyInput(world, localPlayer, currentInput)
        
        // Reconcile with server state when received
        reconcilePredictions(world)
```

##### Procedural Generation System

```pseudo
class ChunkComponent:
    int chunkX, chunkY
    bool isGenerated
    list<EntityID> entities

class ProceduralTerrainSystem extends System:
    map<ChunkCoord, EntityID> loadedChunks
    int viewDistance = 3
    
    function update(World world, float dt):
        // Find player position
        players = world.query([PlayerTag, PositionComponent])
        
        if players.isEmpty():
            return
        
        playerPos = world.getComponent(players[0], PositionComponent)
        playerChunk = worldToChunk(playerPos)
        
        // Load chunks around player
        for x in playerChunk.x - viewDistance to playerChunk.x + viewDistance:
            for y in playerChunk.y - viewDistance to playerChunk.y + viewDistance:
                coord = ChunkCoord(x, y)
                
                if coord not in loadedChunks:
                    generateChunk(world, coord)
        
        // Unload distant chunks
        for coord, chunkEntity in loadedChunks:
            if distance(coord, playerChunk) > viewDistance + 1:
                unloadChunk(world, coord)
    
    function generateChunk(World world, ChunkCoord coord):
        chunk = world.createEntity()
        chunkComp = ChunkComponent(coord.x, coord.y)
        
        // Procedural generation using noise
        seed = coord.x * 1000 + coord.y
        noise = PerlinNoise(seed)
        
        // Generate terrain
        for localX in 0 to chunkSize:
            for localY in 0 to chunkSize:
                worldX = coord.x * chunkSize + localX
                worldY = coord.y * chunkSize + localY
                
                value = noise.get(worldX, worldY)
                
                if value > 0.5:
                    // Spawn tree
                    tree = createTree(worldX, worldY)
                    chunkComp.entities.add(tree)
                else if value < -0.3:
                    // Spawn rock
                    rock = createRock(worldX, worldY)
                    chunkComp.entities.add(rock)
        
        world.addComponent(chunk, chunkComp)
        loadedChunks[coord] = chunk
    
    function unloadChunk(World world, ChunkCoord coord):
        chunkEntity = loadedChunks[coord]
        chunk = world.getComponent(chunkEntity, ChunkComponent)
        
        // Destroy all entities in chunk
        for entity in chunk.entities:
            world.destroyEntity(entity)
        
        world.destroyEntity(chunkEntity)
        loadedChunks.remove(coord)
```

##### Quest System

```pseudo
class QuestComponent:
    list<Quest> activeQuests
    list<Quest> completedQuests

class Quest:
    string id
    string title
    string description
    list<Objective> objectives
    list<Reward> rewards
    QuestState state

class Objective:
    string description
    bool isComplete
    
    abstract function checkCompletion(World world, EntityID player) -> bool

class KillObjective extends Objective:
    string enemyType
    int required
    int current
    
    function checkCompletion(world, player) -> bool:
        return current >= required

class CollectObjective extends Objective:
    string itemType
    int required
    
    function checkCompletion(world, player) -> bool:
        inventory = world.getComponent(player, InventoryComponent)
        return inventory.count(itemType) >= required

class QuestSystem extends System:
    function update(World world, float dt):
        entities = world.query([QuestComponent])
        
        for entity in entities:
            quests = world.getComponent(entity, QuestComponent)
            
            for quest in quests.activeQuests:
                updateQuest(world, entity, quest)
    
    function updateQuest(world, player, quest):
        allComplete = true
        
        for objective in quest.objectives:
            if not objective.isComplete:
                if objective.checkCompletion(world, player):
                    objective.isComplete = true
                    world.emitEvent(ObjectiveCompleteEvent(player, objective))
                else:
                    allComplete = false
        
        if allComplete and quest.state == QuestState.ACTIVE:
            completeQuest(world, player, quest)
    
    function completeQuest(world, player, quest):
        quest.state = QuestState.COMPLETE
        
        // Give rewards
        for reward in quest.rewards:
            reward.give(world, player)
        
        world.emitEvent(QuestCompleteEvent(player, quest))
    
    function onEvent(world, event):
        if event is EnemyKilledEvent:
            updateKillObjectives(world, event)
        if event is ItemCollectedEvent:
            updateCollectObjectives(world, event)
```

##### Save/Load System

```pseudo
class SaveSystem extends System:
    function saveGame(World world, string filename):
        saveData = SerializedWorld()
        
        // Save all entities
        for entity in world.entities:
            entityData = SerializedEntity(entity)
            
            // Save all components
            for componentType in world.entityComponents[entity]:
                component = world.getComponent(entity, componentType)
                entityData.components[componentType] = serializeComponent(component)
            
            saveData.entities.add(entityData)
        
        // Save blackboard/global state
        saveData.blackboard = world.blackboard.serialize()
        
        // Write to file
        writeToFile(filename, saveData.toJSON())
    
    function loadGame(World world, string filename):
        // Clear existing world
        world.clear()
        
        // Read from file
        saveData = parseJSON(readFromFile(filename))
        
        // Load entities
        for entityData in saveData.entities:
            entity = world.createEntityWithId(entityData.id)
            
            // Load components
            for componentType, componentData in entityData.components:
                component = deserializeComponent(componentType, componentData)
                world.addComponent(entity, component)
        
        // Load blackboard
        world.blackboard.deserialize(saveData.blackboard)
    
    function serializeComponent(Component component) -> JSON:
        // Use reflection or manual serialization
        return componentToJSON(component)
    
    function deserializeComponent(ComponentType type, JSON data) -> Component:
        return JSONToComponent(type, data)
```



#### Testing and Debugging

##### Debug System

```pseudo
class DebugSystem extends System:
    bool showColliders = false
    bool showPaths = false
    bool showStats = false
    
    function update(World world, float dt):
        if input.debugToggle():
            showColliders = not showColliders
        
        if showColliders:
            renderColliders(world)
        
        if showPaths:
            renderPaths(world)
        
        if showStats:
            renderStats(world)
    
    function renderColliders(World world):
        entities = world.query([PositionComponent, ColliderComponent])
        
        for entity in entities:
            pos = world.getComponent(entity, PositionComponent)
            col = world.getComponent(entity, ColliderComponent)
            
            debugDraw.circle(pos, col.radius, Color.GREEN)
    
    function renderStats(World world):
        stats = [
            "Entities: " + world.entities.size(),
            "Systems: " + world.systems.size(),
            "FPS: " + calculateFPS()
        ]
        
        debugDraw.text(stats, 10, 10)
```

##### Unit Testing

```pseudo
class ECSTestFramework:
    function testSystem(System system, World world):
        // Setup
        testEntity = setupTestEntity(world)
        
        // Execute
        system.update(world, 0.016)  // Simulate one frame
        
        // Assert
        assertComponentState(world, testEntity)
    
    function testMovement():
        world = new World()
        entity = world.createEntity()
        
        world.addComponent(entity, PositionComponent(0, 0, 0))
        world.addComponent(entity, VelocityComponent(1, 0, 0))
        
        movementSystem = new MovementSystem()
        movementSystem.update(world, 1.0)  // 1 second
        
        pos = world.getComponent(entity, PositionComponent)
        assert(pos.x == 1.0)
        assert(pos.y == 0.0)
```


#### Conclusion

ECS provides a scalable, performant architecture for large games by:
- Separating data (components) from logic (systems)
- Enabling flexible entity composition
- Optimizing for cache-friendly memory access
- Facilitating parallel processing
- Promoting code reusability

*Key Takeaways:*
1. Start with core ECS structure
2. Add systems incrementally as needed
3. Use patterns like pooling and spatial partitioning for performance
4. Leverage events for loose coupling
5. Profile and optimize bottlenecks
6. Test systems in isolation

*Next Steps:*
- Implement basic ECS framework in your language of choice
- Start with simple systems (movement, rendering)
- Add gameplay systems (combat, inventory)
- Optimize with advanced patterns
- Build editor tools for productivity
