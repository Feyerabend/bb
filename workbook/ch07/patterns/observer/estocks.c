#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Fwd decl
typedef struct Observer Observer;
typedef struct Stock Stock;

// Observer interface (function pointer for update)
typedef void (*UpdateFunc)(Observer*, float);

// Observer structure
struct Observer {
    void* data;           // Generic pointer for observer-specific data
    UpdateFunc update;    // Function pointer for update method
    char* type;           // Observer type name
};

// Subject (Stock) structure
struct Stock {
    float price;          // State: stock price
    Observer** observers; // Array of pointers to observers
    int observer_count;   // Number of observers
    int max_observers;    // Capacity of observer array
};

// Configuration structure for observer types
typedef struct {
    char* type_name;
    UpdateFunc update_func;
} ObserverConfig;

// Concrete Observer: Investor
typedef struct {
    char* name;     // Investor name
} Investor;

// Concrete Observer: Bank
typedef struct {
    char* bank_name;
    float threshold;    // Price threshold for notifications
} Bank;

// Concrete Observer: News Agency
typedef struct {
    char* agency_name;
    int priority;       // Priority level
} NewsAgency;

// Update function for Investor
void investor_update(Observer* observer, float price) {
    Investor* investor = (Investor*)observer->data;
    printf("[INVESTOR] %s received update: Stock price is now %.2f\n", 
           investor->name, price);
}

// Update function for Bank
void bank_update(Observer* observer, float price) {
    Bank* bank = (Bank*)observer->data;
    if (price > bank->threshold) {
        printf("[BANK] %s ALERT: Stock price %.2f exceeds threshold %.2f\n", 
               bank->bank_name, price, bank->threshold);
    } else {
        printf("[BANK] %s monitoring: Stock price %.2f (threshold: %.2f)\n", 
               bank->bank_name, price, bank->threshold);
    }
}

// Update function for News Agency
void news_agency_update(Observer* observer, float price) {
    NewsAgency* agency = (NewsAgency*)observer->data;
    if (agency->priority > 5) {
        printf("[NEWS-HIGH] %s BREAKING: Stock price now %.2f!\n", 
               agency->agency_name, price);
    } else {
        printf("[NEWS] %s reports: Stock price updated to %.2f\n", 
               agency->agency_name, price);
    }
}

// Registry of available observer types
ObserverConfig observer_registry[] = {
    {"investor", investor_update},
    {"bank", bank_update},
    {"news", news_agency_update}
};
const int registry_size = sizeof(observer_registry) / sizeof(ObserverConfig);

// Find update function by type name
UpdateFunc find_update_function(const char* type_name) {
    for (int i = 0; i < registry_size; i++) {
        if (strcmp(observer_registry[i].type_name, type_name) == 0) {
            return observer_registry[i].update_func;
        }
    }
    return NULL;
}

// Create observer data based on type
void* create_observer_data(const char* type, const char* name, const char* extra_param) {
    if (strcmp(type, "investor") == 0) {
        Investor* investor = (Investor*)malloc(sizeof(Investor));
        investor->name = (char*)malloc(strlen(name) + 1);
        strcpy(investor->name, name);
        return investor;
    } else if (strcmp(type, "bank") == 0) {
        Bank* bank = (Bank*)malloc(sizeof(Bank));
        bank->bank_name = (char*)malloc(strlen(name) + 1);
        strcpy(bank->bank_name, name);
        bank->threshold = extra_param ? atof(extra_param) : 100.0;
        return bank;
    } else if (strcmp(type, "news") == 0) {
        NewsAgency* agency = (NewsAgency*)malloc(sizeof(NewsAgency));
        agency->agency_name = (char*)malloc(strlen(name) + 1);
        strcpy(agency->agency_name, name);
        agency->priority = extra_param ? atoi(extra_param) : 5;
        return agency;
    }
    return NULL;
}

// Free observer data based on type
void free_observer_data(Observer* observer) {
    if (strcmp(observer->type, "investor") == 0) {
        Investor* investor = (Investor*)observer->data;
        free(investor->name);
        free(investor);
    } else if (strcmp(observer->type, "bank") == 0) {
        Bank* bank = (Bank*)observer->data;
        free(bank->bank_name);
        free(bank);
    } else if (strcmp(observer->type, "news") == 0) {
        NewsAgency* agency = (NewsAgency*)observer->data;
        free(agency->agency_name);
        free(agency);
    }
}

// Create an observer
Observer* create_observer(const char* type, const char* name, const char* extra_param) {
    UpdateFunc update_func = find_update_function(type);
    if (!update_func) {
        printf("Error: Unknown observer type '%s'\n", type);
        return NULL;
    }
    
    void* data = create_observer_data(type, name, extra_param);
    if (!data) {
        printf("Error: Failed to create observer data for type '%s'\n", type);
        return NULL;
    }
    
    Observer* observer = (Observer*)malloc(sizeof(Observer));
    observer->data = data;
    observer->update = update_func;
    observer->type = (char*)malloc(strlen(type) + 1);
    strcpy(observer->type, type);
    
    return observer;
}

// Create a stock (subject)
Stock* create_stock(float initial_price) {
    Stock* stock = (Stock*)malloc(sizeof(Stock));
    stock->price = initial_price;
    stock->observer_count = 0;
    stock->max_observers = 50;  // Increased capacity
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
    printf("\n=== Stock price updated to %.2f ===\n", price);
    notify_observers(stock);
    printf("=== End of notifications ===\n\n");
}

// Load observers from configuration file
int load_observers_from_config(Stock* stock, const char* config_file) {
    FILE* file = fopen(config_file, "r");
    if (!file) {
        printf("Error: Cannot open configuration file '%s'\n", config_file);
        return 0;
    }
    
    char line[256];
    int observers_loaded = 0;
    
    printf("Loading observers from configuration file...\n");
    
    while (fgets(line, sizeof(line), file)) {
        // Skip empty lines and comments
        if (line[0] == '\n' || line[0] == '#') {
            continue;
        }
        
        // Remove newline character
        line[strcspn(line, "\n")] = 0;
        
        // Parse line: type,name,extra_param
        char* type = strtok(line, ",");
        char* name = strtok(NULL, ",");
        char* extra_param = strtok(NULL, ",");
        
        if (type && name) {
            Observer* observer = create_observer(type, name, extra_param);
            if (observer) {
                attach_observer(stock, observer);
                observers_loaded++;
                printf("  Loaded %s observer: %s", type, name);
                if (extra_param) {
                    printf(" (param: %s)", extra_param);
                }
                printf("\n");
            }
        }
    }
    
    fclose(file);
    printf("Successfully loaded %d observers from configuration.\n\n", observers_loaded);
    return observers_loaded;
}

// Clean up
void destroy_stock(Stock* stock) {
    free(stock->observers);
    free(stock);
}

void destroy_observer(Observer* observer) {
    if (observer) {
        free_observer_data(observer);
        free(observer->type);
        free(observer);
    }
}

// Create a sample configuration file
void create_sample_config() {
    FILE* file = fopen("observers.cfg", "w");
    if (file) {
        fprintf(file, "# Observer Configuration File\n");
        fprintf(file, "# Format: type,name,extra_parameter\n");
        fprintf(file, "# Available types: investor, bank, news\n\n");
        fprintf(file, "investor,Alice,\n");
        fprintf(file, "investor,Bob,\n");
        fprintf(file, "bank,First National Bank,105.0\n");
        fprintf(file, "bank,City Bank,95.0\n");
        fprintf(file, "news,Financial Times,8\n");
        fprintf(file, "news,Local News,3\n");
        fprintf(file, "investor,Charlie,\n");
        fclose(file);
        printf("Sample configuration file 'observers.cfg' created.\n");
    }
}

int main() {
    printf("=== Dynamic Observer Pattern Demo ===\n\n");
    
    // Create sample configuration file if it doesn't exist
    FILE* test_file = fopen("observers.cfg", "r");
    if (!test_file) {
        create_sample_config();
    } else {
        fclose(test_file);
    }
    
    // Create stock (subject)
    Stock* stock = create_stock(100.0);
    
    // Load observers from configuration file
    int loaded = load_observers_from_config(stock, "observers.cfg");
    
    if (loaded == 0) {
        printf("No observers loaded. Exiting.\n");
        destroy_stock(stock);
        return 1;
    }
    
    // Simulate stock price changes
    set_stock_price(stock, 105.5);
    set_stock_price(stock, 98.0);
    set_stock_price(stock, 110.0);
    set_stock_price(stock, 92.0);
    
    // Clean up all observers
    printf("Cleaning up observers...\n");
    for (int i = 0; i < stock->observer_count; i++) {
        destroy_observer(stock->observers[i]);
    }
    
    destroy_stock(stock);
    
    printf("\nDemo completed successfully!\n");
    return 0;
}


// An extended version of the Observer Pattern in C, demonstrating dynamic
// observer registration, multiple observer types, and configuration file loading.

// This code allows for dynamic observer management and demonstrates how to
// handle different observer types with specific behaviours. It includes a sample
// configuration file for observer setup and showcases how to notify observers
// of state changes in a subject (stock) while maintaining clean memory management.

// The code is designed to be modular and extensible, allowing for easy addition of
// new observer types and behaviors in the future. It also includes error handling
// for observer creation and configuration file loading, ensuring robustness in
// real-world applications. The observer types include investors, banks, and news
// agencies, each with its own update behaviour based on the stock price changes.

