/**
 * EVENT-DRIVEN PROGRAMMING PATTERNS
 * This file demonstrates common implementation patterns used in event-driven programming
 */

// OBSERVER PATTERN
console.log(" OBSERVER PATTERN ");

class Subject {
  constructor() {
    this.observers = [];
  }

  addObserver(observer) {
    this.observers.push(observer);
  }

  removeObserver(observer) {
    this.observers = this.observers.filter(obs => obs !== observer);
  }

  notify(data) {
    this.observers.forEach(observer => observer.update(data));
  }
}

class Observer {
  constructor(name) {
    this.name = name;
  }

  update(data) {
    console.log(`${this.name} received update: ${data}`);
  }
}

// example
const weatherStation = new Subject();

const phoneApp = new Observer("Phone App");
const dashboard = new Observer("Weather Dashboard");
const newsService = new Observer("News Service");

weatherStation.addObserver(phoneApp);
weatherStation.addObserver(dashboard);
weatherStation.addObserver(newsService);

// when weather changes, all observers are notified
weatherStation.notify("Temperature: 72°F, Sunny");

// remove one observer
weatherStation.removeObserver(newsService);
weatherStation.notify("Temperature: 65°F, Cloudy");


// PUBLISH/SUBSCRIBE (PUB/SUB) PATTERN
console.log("\n PUBLISH/SUBSCRIBE PATTERN ");

class EventBus {
  constructor() {
    this.subscribers = {};
  }

  subscribe(event, callback) {
    if (!this.subscribers[event]) {
      this.subscribers[event] = [];
    }
    this.subscribers[event].push(callback);
    
    return () => this.unsubscribe(event, callback); // return unsubscribe function
  }

  unsubscribe(event, callback) {
    if (this.subscribers[event]) {
      this.subscribers[event] = this.subscribers[event].filter(cb => cb !== callback);
    }
  }

  publish(event, data) {
    if (this.subscribers[event]) {
      this.subscribers[event].forEach(callback => callback(data));
    }
  }
}

// example
const eventBus = new EventBus();

// multiple components can subscribe to different events
const userLoggedInHandler = (user) => {
  console.log(`User logged in: ${user.name}`);
};

const cartUpdatedHandler = (cart) => {
  console.log(`Cart updated: ${cart.items.length} items, total: $${cart.total}`);
};

const orderPlacedHandler = (order) => {
  console.log(`New order: #${order.id}, amount: $${order.amount}`);
};

// subscribe to events
eventBus.subscribe('USER_LOGGED_IN', userLoggedInHandler);
eventBus.subscribe('CART_UPDATED', cartUpdatedHandler);
eventBus.subscribe('ORDER_PLACED', orderPlacedHandler);

// later in app ..
eventBus.publish('USER_LOGGED_IN', { name: 'Alice', id: 123 });
eventBus.publish('CART_UPDATED', { items: [{ id: 1, name: 'Book' }, { id: 2, name: 'Pen' }], total: 25.99 });
eventBus.publish('ORDER_PLACED', { id: 'ORD-789', amount: 25.99, userId: 123 });


// EVENT DELEGATION
console.log("\n EVENT DELEGATION PATTERN ");

// This pattern is typically used in DOM manipulation
// Below is a pseudocode example showing how it would be implemented in a browser

/*
// Instead of attaching event handlers to each button:
document.getElementById('button1').addEventListener('click', handleClick);
document.getElementById('button2').addEventListener('click', handleClick);
document.getElementById('button3').addEventListener('click', handleClick);

// Use event delegation - attach one handler to the parent:
document.getElementById('button-container').addEventListener('click', function(event) {
  // Check if the clicked element is a button
  if (event.target.tagName === 'BUTTON') {
    // Get button-specific data
    const buttonId = event.target.id;
    const action = event.target.dataset.action;
    
    console.log(`Button ${buttonId} clicked with action: ${action}`);
    
    // Handle the action
    switch (action) {
      case 'save':
        saveData();
        break;
      case 'delete':
        deleteItem();
        break;
      case 'update':
        updateRecord();
        break;
    }
  }
});
*/

// JS implementation example (not! using DOM)
class UIComponent {
  constructor() {
    this.elements = [];
    this.handlers = {};
  }

  addElement(element) {
    this.elements.push(element);
  }

  on(eventType, handler) {
    this.handlers[eventType] = handler;
  }

  // simulate a click on a specific element
  triggerEvent(elementId, eventType) {
    const element = this.elements.find(el => el.id === elementId);
    if (element && this.handlers[eventType]) {
      console.log(`Event '${eventType}' triggered on element '${element.id}'`);
      // handler is called with the element as the context and event info
      this.handlers[eventType](element);
    }
  }
}

// example
const menuContainer = new UIComponent();

// add multiple menu items
menuContainer.addElement({ id: 'menu-home', text: 'Home', action: 'navigate' });
menuContainer.addElement({ id: 'menu-products', text: 'Products', action: 'navigate' });
menuContainer.addElement({ id: 'menu-contact', text: 'Contact', action: 'navigate' });

// single handler for all menu items
menuContainer.on('click', function(element) {
  console.log(`Navigating to: ${element.text} page`);
});

// simulate clicks
menuContainer.triggerEvent('menu-home', 'click');
menuContainer.triggerEvent('menu-products', 'click');


// PROMISE-BASED EVENTS
console.log("\n PROMISE-BASED EVENTS PATTERN ");

class AsyncEventEmitter {
  constructor() {
    this.events = {};
  }

  on(event, listener) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(listener);
  }

  emit(event, ...args) {
    if (!this.events[event]) return Promise.resolve([]);
    
    const promises = this.events[event].map(listener => {
      try {
        return Promise.resolve(listener(...args));
      } catch (error) {
        return Promise.reject(error);
      }
    });
    
    return Promise.all(promises);
  }
}

// example
const asyncEventSystem = new AsyncEventEmitter();

// register event handlers
asyncEventSystem.on('data-received', async (data) => {
  console.log('Processing data...');
  // simulate async operation
  await new Promise(resolve => setTimeout(resolve, 100));
  return `Processed: ${data}`;
});

asyncEventSystem.on('data-received', async (data) => {
  console.log('Saving data to database...');
  // simulate async operation
  await new Promise(resolve => setTimeout(resolve, 200));
  return 'Data saved';
});

// trigger event and handle results
console.log('Emitting event...');
asyncEventSystem.emit('data-received', 'User profile data')
  .then(results => {
    console.log('All handlers completed with results:', results);
  })
  .catch(error => {
    console.error('Error in event handler:', error);
  });


// STATE MACHINE WITH EVENTS
console.log("\n STATE MACHINE PATTERN ");

class StateMachine {
  constructor() {
    this.state = 'idle';
    this.transitions = {
      idle: { start: 'running' },
      running: { pause: 'paused', stop: 'idle' },
      paused: { resume: 'running', stop: 'idle' }
    };
    this.listeners = {};
  }

  addListener(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  notify(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }

  trigger(action) {
    const currentState = this.state;
    const nextState = this.transitions[currentState]?.[action];
    
    if (nextState) {
      console.log(`Transitioning from '${currentState}' to '${nextState}' due to '${action}' action`);
      this.state = nextState;
      this.notify('stateChanged', { 
        from: currentState, 
        to: nextState, 
        action 
      });
      return true;
    } else {
      console.log(`Action '${action}' not allowed in state '${currentState}'`);
      return false;
    }
  }

  getState() {
    return this.state;
  }
}

// example
const playerStateMachine = new StateMachine();

// add state change listener
playerStateMachine.addListener('stateChanged', (data) => {
  console.log(`Player state changed: ${data.from} -> ${data.to}`);
  
  if (data.to === 'running') {
    console.log('Player started playing music');
  } else if (data.to === 'paused') {
    console.log('Player paused music');
  } else if (data.to === 'idle') {
    console.log('Player stopped music');
  }
});

// trigger state transitions
playerStateMachine.trigger('start');  // idle -> running
playerStateMachine.trigger('pause');  // running -> paused
playerStateMachine.trigger('stop');   // paused -> idle
//playerStateMachine.trigger('resume'); // paused -> running
