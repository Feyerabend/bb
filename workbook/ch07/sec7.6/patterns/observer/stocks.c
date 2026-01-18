#include <stdio.h>
#include <stdlib.h>

// Forward declarations
typedef struct Observer Observer;
typedef struct Stock Stock;

// Observer interface (function pointer for update)
typedef void (*UpdateFunc)(Observer*, float);

// Observer structure
struct Observer {
    void* data;           // Generic pointer for observer-specific data
    UpdateFunc update;    // Function pointer for update method
};

// Subject (Stock) structure
struct Stock {
    float price;          // State: stock price
    Observer** observers; // Array of pointers to observers
    int observer_count;   // Number of observers
    int max_observers;    // Capacity of observer array
};

// Concrete Observer: Investor
typedef struct {
    const char* name;     // Investor name
} Investor;

// Update function for Investor
void investor_update(Observer* observer, float price) {
    Investor* investor = (Investor*)observer->data;
    printf("%s received update: Stock price is now %.2f\n", investor->name, price);
}

// Create an observer
Observer* create_observer(void* data, UpdateFunc update) {
    Observer* observer = (Observer*)malloc(sizeof(Observer));
    observer->data = data;
    observer->update = update;
    return observer;
}

// Create a stock (subject)
Stock* create_stock(float initial_price) {
    Stock* stock = (Stock*)malloc(sizeof(Stock));
    stock->price = initial_price;
    stock->observer_count = 0;
    stock->max_observers = 10;
    stock->observers = (Observer**)malloc(stock->max_observers * sizeof(Observer*));
    return stock;
}

// Attach an observer to the stock
void attach_observer(Stock* stock, Observer* observer) {
    if (stock->observer_count < stock->max_observers) {
        stock->observers[stock->observer_count++] = observer;
    } else {
        printf("Cannot attach more observers, limit reached.\n");
    }
}

// Detach an observer from the stock
void detach_observer(Stock* stock, Observer* observer) {
    for (int i = 0; i < stock->observer_count; i++) {
        if (stock->observers[i] == observer) {
            stock->observers[i] = stock->observers[--stock->observer_count];
            break;
        }
    }
}

// Notify all observers of a state change
void notify_observers(Stock* stock) {
    for (int i = 0; i < stock->observer_count; i++) {
        stock->observers[i]->update(stock->observers[i], stock->price);
    }
}

// Update stock price and notify observers
void set_stock_price(Stock* stock, float price) {
    stock->price = price;
    printf("Stock price updated to %.2f\n", price);
    notify_observers(stock);
}

// Clean up
void destroy_stock(Stock* stock) {
    free(stock->observers);
    free(stock);
}

void destroy_observer(Observer* observer) {
    free(observer);
}

int main() {
    // Create stock (subject)
    Stock* stock = create_stock(100.0);

    // Create investors (observers)
    Investor investor1 = {"Alice"};
    Investor investor2 = {"Bob"};
    Observer* observer1 = create_observer(&investor1, investor_update);
    Observer* observer2 = create_observer(&investor2, investor_update);

    // Attach observers
    attach_observer(stock, observer1);
    attach_observer(stock, observer2);

    // Change stock price
    set_stock_price(stock, 105.5);
    set_stock_price(stock, 98.0);

    // Detach one observer
    detach_observer(stock, observer1);
    printf("Detached Alice from stock updates.\n");

    // Change stock price again
    set_stock_price(stock, 110.0);

    // Clean up
    destroy_observer(observer1);
    destroy_observer(observer2);
    destroy_stock(stock);

    return 0;
}