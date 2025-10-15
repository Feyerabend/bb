
## Simple Game Arcitecture

This is a very *simplified entity-manager pattern*,
not a true Entity-Component-System:

*This Approach (Entity-Manager):*
- Entities use *inheritance* (Player extends Entity)
- Logic lives *inside entity classes* (Player has input logic)
- Simpler, more intuitive for small games
- Less flexible but easier to understand

*True ECS:*
- Entities are just *IDs* (no logic or data)
- *Components* are pure data (PositionComponent, VelocityComponent)
- *Systems* contain all logic (MovementSystem, RenderSystem)
- Data-oriented design for performance at scale
- More complex but extremely flexible

*When to upgrade to full ECS:* When you have a 1000 entities,
need data caching optimisation, or want to compose entities from
interchangeable parts without inheritance hierarchies.


### Core  (CRC cards)

```
║ ENTITY MANAGER
║ Responsibilities:
║  - Lifecycle: create, destroy, store all entities
║  - Update all entities each frame
║  - Query/lookup entities by type or ID
║ Collaborates: Entity, Player, Sprite, Enemy


║ ENTITY (Base)
║ Responsibilities:
║  - ID, position, velocity, active state
║  - update(dt): apply velocity → position (movement physics)
║  - render(): interface for drawing
║ Collaborates: EntityManager, subclasses (Player/Sprite)


║ PLAYER / SPRITE / ENEMY : Entity
║ Player:
║  - Process input → set velocity → call super.update()
║  - Render player sprite/shape
║  - Collaborates: InputHandler
║ Sprite (static):
║  - No movement (velocity = 0)
║  - Just renders visual
║ Enemy (AI):
║  - AI logic → set velocity → call super.update()
║  - Bounce/patrol behavior
```

### Support Systems (2 Cards)

```
║ INPUT HANDLER
║ - Poll keyboard/mouse, store key states
║ - Provide input queries to Player
║ Collaborates: Player, GameLoop


║ RENDERER
║ - Clear screen, draw all entities, present frame
║ - Query EntityManager for drawable entities
║ Collaborates: EntityManager, Entity
```




#### Movement Location: *Entity Base Class*

```
Entity stores:     position, velocity
Entity.update():   position += velocity * dt

Subclasses set:    velocity (based on input/AI)
Subclasses call:   super.update() to apply movement
```

#### Flow
```
GameLoop
   |
   ├─- InputHandler ──-- Player.update()
   │                       |
   ├─- EntityManager ──- [Entity.update() for all]
   │                       |
   └─- Renderer ──────-- [Entity.render() for all]
```

#### Memory Management

- *EntityManager* owns all entities
- Array/vector storage for cache efficiency
- `createEntity()` / `destroyEntity()` for lifecycle
- Optional: object pooling for reuse



### Implementation Pattern (Pseudocode)

```pseudocode
class Entity:
    position, velocity, id, active
    update(dt):
        position += velocity * dt

class Player extends Entity:
    update(dt, input):
        if input.left: velocity.x = -speed
        super.update(dt)

class EntityManager:
    entities = []
    
    createEntity(type, args):
        entity = new type(args)
        entities.add(entity)
        return entity
    
    update(dt, input):
        for entity in entities:
            entity.update(dt, input)

class Game:
    entityManager = new EntityManager()
    inputHandler = new InputHandler()
    renderer = new Renderer()
    
    loop():
        input = inputHandler.poll()
        entityManager.update(dt, input)
        renderer.render(entityManager)
```





# Entity-Component System Explained

game architecture pattern:
- *Entity*: Game objects (players, enemies, bullets)
- *EntityManager*: Container that handles all entities
- *Game*: Main loop that coordinates everything


```
Game Loop:
1. Get input (keyboard/mouse)
2. Update all entities (move, check collisions)
3. Render everything to screen
```

*Entity* = Data + Behavior
- Stores position, velocity, ID
- Updates itself each frame

*Player* = Special Entity
- Responds to input (arrow keys, etc.)
- Calls parent Entity's update for movement

*EntityManager* = Collection Manager
- Factory: Creates new entities
- Updates all entities each frame
- Central registry



Good
- Games with many similar objects
- When you need centralized entity management
- Simple to medium complexity games

Not ideal
- Very large-scale games (needs optimization)
- Projects requiring maximum flexibility


Extend

### 1. Add More Entity Types
```javascript
class Enemy extends Entity:
    update(dt):
        // AI logic here
        position.x += sin(time) * speed
        super.update(dt)

class Bullet extends Entity:
    lifespan = 3.0
    update(dt):
        lifespan -= dt
        if lifespan <= 0:
            active = false
        super.update(dt)
```

### 2. Add Components (Composition over Inheritance)
```javascript
class Entity:
    components = []
    addComponent(component)
    update(dt):
        for component in components:
            component.update(dt)

// Now mix and match:
player.addComponent(new InputComponent())
player.addComponent(new PhysicsComponent())
player.addComponent(new SpriteComponent())
```

### 3. Add Systems
```javascript
class CollisionSystem:
    checkCollisions(entities)

class RenderSystem:
    render(entities)

// In Game loop:
collisionSystem.check(entityManager.entities)
renderSystem.render(entityManager.entities)
```

### 4. Object Pooling (Performance)
```javascript
class EntityManager:
    pool = []
    
    getEntity(type):
        entity = pool.findInactive()
        if entity:
            entity.active = true
            return entity
        return createEntity(type)
    
    releaseEntity(entity):
        entity.active = false
        // Reuse later
```

### 5. Event System
```javascript
class EventBus:
    listeners = {}
    
    emit(event, data)
    on(event, callback)

// Usage:
eventBus.on("collision", handleCollision)
eventBus.emit("collision", {entity1, entity2})
```

