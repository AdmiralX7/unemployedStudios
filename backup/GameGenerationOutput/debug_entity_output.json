```javascript
// game_entities.js
//
// Standalone game entity system for HTML5 games
// Provides a comprehensive entity-component-system implementation
//
// This file is designed for backward compatibility and can function
// independently when included directly into an HTML page or be utilized
// in a template integration approach with GameLogic extensions.
//
// ****************************************************************************
// This implementation assumes all component classes have serialize and deserialize methods
// and are defined globally. You may need to adjust component handling
// and class naming to align with your specific game needs.
// ****************************************************************************

// Entity class
class Entity {
    constructor() {
        this.id = Entity.generateUniqueId();
        this.components = new Map();
    }

    addComponent(component) {
        this.components.set(component.constructor.name, component);
    }

    removeComponent(componentName) {
        this.components.delete(componentName);
    }

    getComponent(componentName) {
        return this.components.get(componentName);
    }

    static generateUniqueId() {
        return '_' + Math.random().toString(36).substr(2, 9);
    }
}

// EntityManager class
class EntityManager {
    constructor() {
        this.entities = new Map();
    }

    initialize() {
        // Initialization logic if any
    }

    createEntity() {
        const entity = new Entity();
        this.entities.set(entity.id, entity);
        return entity;
    }
    
    deleteEntity(entityId) {
        this.entities.delete(entityId);
    }
    
    getEntity(entityId) {
        return this.entities.get(entityId);
    }
}

// PhysicsSystem class
class PhysicsSystem {
    constructor(entityManager) {
        this.entityManager = entityManager;
    }

    update(deltaTime) {
        for (const entity of this.entityManager.entities.values()) {
            const position = entity.getComponent('PositionComponent');
            const velocity = entity.getComponent('VelocityComponent');

            if (position && velocity) {
                position.x += velocity.vx * deltaTime;
                position.y += velocity.vy * deltaTime;
                
                this.handleCollisions(entity);
            }
        }
    }

    handleCollisions(entity) {
        const shape = entity.getComponent('ShapeComponent');
        if (!shape) return;
        
        for (const other of this.entityManager.entities.values()) {
            if (entity === other) continue;

            const otherShape = other.getComponent('ShapeComponent');
            if (otherShape && this.checkCollision(shape, otherShape)) {
                const velocity = entity.getComponent('VelocityComponent');
                if (velocity) {
                    velocity.vx *= -1;
                    velocity.vy *= -1;
                }
            }
        }
    }

    checkCollision(shapeA, shapeB) {
        if (shapeA.shape === 'circle' && shapeB.shape === 'circle') {
            // Example collision logic
            return false; // Placeholder
        }
        return false;
    }
}

// AISystem class
class AISystem {
    constructor(entityManager) {
        this.entityManager = entityManager;
    }

    update(deltaTime) {
        for (const entity of this.entityManager.entities.values()) {
            const aiComponent = entity.getComponent('AIComponent');
            if (aiComponent) {
                this.processAI(entity, aiComponent, deltaTime);
            }
        }
    }

    processAI(entity, aiComponent, deltaTime) {
        switch (aiComponent.state) {
            case 'patrolling':
                break;
            case 'chasing':
                break;
        }
    }
}

// InteractiveSystem class
class InteractiveSystem {
    constructor(entityManager) {
        this.entityManager = entityManager;
    }

    processInteractions(input) {
        for (const entity of this.entityManager.entities.values()) {
            const interactiveComponent = entity.getComponent('InteractiveComponent');
            if (interactiveComponent) {
                this.handleInput(entity, interactiveComponent, input);
            }
        }
    }

    handleInput(entity, interactiveComponent, input) {
        if (input === 'activate') {
            // Trigger specific actions
        }
    }
}

// ExtendedGameLogic class for system integration
class ExtendedGameLogic extends GameLogic {
    constructor() {
        super();
        this.entityManager = new EntityManager();
        this.physicsSystem = new PhysicsSystem(this.entityManager);
        this.aiSystem = new AISystem(this.entityManager);
        this.interactiveSystem = new InteractiveSystem(this.entityManager);
    }

    initialize() {
        super.initialize();
        this.entityManager.initialize();
        console.log('Entity system initialized');
    }

    update(deltaTime) {
        super.update(deltaTime);
        this.physicsSystem.update(deltaTime);
        this.aiSystem.update(deltaTime);
    }

    handleInput(input) {
        super.handleInput(input);
        this.interactiveSystem.processInteractions(input);
    }
}

// Serialization and Deserialization tools
function serializeEntityManager(entityManager) {
    const serializedEntities = [];
    for (const entity of entityManager.entities.values()) {
        const serializedComponents = {};
        for (const [name, component] of entity.components.entries()) {
            serializedComponents[name] = component.serialize();
        }
        serializedEntities.push({ id: entity.id, components: serializedComponents });
    }
    return JSON.stringify(serializedEntities);
}

function deserializeEntityManager(data, entityManager) {
    const entitiesData = JSON.parse(data);
    for (const entityData of entitiesData) {
        const entity = entityManager.createEntity();
        entity.id = entityData.id;
        for (const [name, componentData] of Object.entries(entityData.components)) {
            const component = new window[name]();
            component.deserialize(componentData);
            entity.addComponent(component);
        }
    }
}

// Note: This standalone file is ready to be integrated into your existing HTML5 game
// setup for backward compatibility, providing robust entity management and system
// capabilities outside of the template. Adapt and expand as needed for new functionality.
```