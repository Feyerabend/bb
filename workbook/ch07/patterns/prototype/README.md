
## Prototype Pattern

RenderingConfig Class:

Created a proper RenderingConfig class to replace the dictionary-based approach
Added a clone() method that creates deep copies using copy.deepcopy()
This enables creating new configurations based on existing ones


Config Prototypes Registry:

Added a ConfigPrototypes class that serves as a registry for predefined configuration templates
Includes three prototype configurations: "default", "high-res", and "minimalist"
Each prototype can be cloned and customized as needed


Builder Integration with Prototypes:

Modified the RenderingConfigBuilder to accept an optional prototype parameter
When a prototype is provided, the builder starts with a clone of that prototype
This combines the flexibility of the Builder pattern with the efficiency of the Prototype pattern


Example:

Demonstrated how to clone and customize a prototype configuration
Created a high-resolution variant directly from the prototype without using the builder

