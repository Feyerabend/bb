/* Graphics VM - Interprets a custom language for creating graphics */

 #include <stdio.h>
 #include <stdlib.h>
 #include <string.h>
 #include <math.h>
 #include <ctype.h>
 #include <stdbool.h>
 
 #define DEFAULT_WIDTH 400
 #define DEFAULT_HEIGHT 400
 #define MAX_COLOR 255
 #define MAX_LINE_LENGTH 256
 #define MAX_TOKENS 20
 #define MAX_SCRIPT_SIZE 10240  // max script file size (10KB)
 #define INITIAL_CAPACITY 16    // initial capacity for dynamic arrays
 
 typedef struct Color {
     int r, g, b;
 } Color;
 
 typedef struct Point {
     int x, y;
 } Point;
 
 // fwd decl
 struct GraphicComponent;
 struct CompositeGroup;
 
 // function pointer types for graphic operations
 typedef void (*RenderFunc)(struct GraphicComponent*, int***);
 typedef void (*FreeFunc)(struct GraphicComponent*);
 
 // base "interface" for all graphics components
 typedef struct GraphicComponent {
     char* name;
     RenderFunc render;
     FreeFunc free;
     void* data; // specific shape data
 } GraphicComponent;
 
 typedef struct Circle {
     Point center;
     int radius;
     Color color;
 } Circle;
 
 typedef struct Rectangle {
     Point topLeft;
     int width;
     int height;
     Color color;
 } Rectangle;
 
 typedef struct Triangle {
     Point p1, p2, p3;
     Color color;
 } Triangle;
 
 // Composite - Container for multiple graphic components
 typedef struct CompositeGroup {
     GraphicComponent** children;
     int childCount;
     int capacity;
 } CompositeGroup;
 
 // AST node types
 typedef enum {
     NODE_CANVAS,
     NODE_CIRCLE,
     NODE_RECTANGLE,
     NODE_TRIANGLE,
     NODE_GROUP_START,
     NODE_GROUP_END,
     NODE_RENDER
 } NodeType;
 
 // AST node structure
 typedef struct ASTNode {
     NodeType type;
     char** params;       // array of parameter strings
     int paramCount;      // number of parameters
     struct ASTNode* next; // linked list of nodes
 } ASTNode;
 
 // Script AST structure
 typedef struct ScriptAST {
     ASTNode* head;       // first node
     ASTNode* tail;       // last node for easy appending
     int nodeCount;       // total number of nodes
 } ScriptAST;
 
 // VM context
 typedef struct {
     int width;
     int height;
     int*** image;
     GraphicComponent** components;   // dynamic array of components
     int componentCount;
     int componentCapacity;
     GraphicComponent** groupStack;   // dynamic array for group stack
     int groupStackPtr;
     int groupStackCapacity;
     ScriptAST* ast;      // parsed AST
 } VM;
 
 // memory tracking (optional but helpful)
 typedef struct MemoryBlock {
     void* ptr;
     size_t size;
     const char* description;
     struct MemoryBlock* next;
 } MemoryBlock;
 
 typedef struct MemoryTracker {
     MemoryBlock* head;
     size_t totalAllocated;
     size_t totalFreed;
     int blockCount;
 } MemoryTracker;
 
 // global memory tracker
 MemoryTracker g_memTracker = { NULL, 0, 0, 0 };
 
 // memory management
 void* trackedMalloc(size_t size, const char* description) {
     void* ptr = malloc(size);
     if (!ptr) {
         fprintf(stderr, "Memory allocation failed for %s\n", description);
         return NULL;
     }
     
     MemoryBlock* block = (MemoryBlock*)malloc(sizeof(MemoryBlock));
     if (!block) {
         free(ptr);
         fprintf(stderr, "Memory tracking allocation failed\n");
         return NULL;
     }
     
     block->ptr = ptr;
     block->size = size;
     block->description = description;
     block->next = g_memTracker.head;
     g_memTracker.head = block;
     
     g_memTracker.totalAllocated += size;
     g_memTracker.blockCount++;
     
     return ptr;
 }
 
 void trackedFree(void* ptr) {
     if (!ptr) return;
     
     MemoryBlock* curr = g_memTracker.head;
     MemoryBlock* prev = NULL;
     
     while (curr && curr->ptr != ptr) {
         prev = curr;
         curr = curr->next;
     }
     
     if (curr) {
         g_memTracker.totalFreed += curr->size;
         
         if (prev) {
             prev->next = curr->next;
         } else {
             g_memTracker.head = curr->next;
         }
         
         g_memTracker.blockCount--;
         free(curr);
     }
     
     free(ptr);
 }
 
 void printMemoryStats() {
     printf("Memory Statistics:\n");
     printf("  Total Blocks: %d\n", g_memTracker.blockCount);
     printf("  Total Allocated: %zu bytes\n", g_memTracker.totalAllocated);
     printf("  Total Freed: %zu bytes\n", g_memTracker.totalFreed);
     printf("  Current Usage: %zu bytes\n", g_memTracker.totalAllocated - g_memTracker.totalFreed);
     
     if (g_memTracker.blockCount > 0) {
         printf("  Unfreed blocks:\n");
         MemoryBlock* curr = g_memTracker.head;
         while (curr) {
             printf("    %p (%zu bytes): %s\n", curr->ptr, curr->size, curr->description);
             curr = curr->next;
         }
     }
 }
 
 // utils
 int isInCircle(int x, int y, Circle* circle) {
     int dx = x - circle->center.x;
     int dy = y - circle->center.y;
     return (dx * dx + dy * dy <= circle->radius * circle->radius);
 }
 
 int isInRectangle(int x, int y, Rectangle* rect) {
     return (x >= rect->topLeft.x && x < rect->topLeft.x + rect->width &&
             y >= rect->topLeft.y && y < rect->topLeft.y + rect->height);
 }
 
 // check if point (x, y) is inside triangle defined by points p1, p2, p3
 // using barycentric coordinates
 int isInTriangle(int x, int y, Triangle* tri) {
     Point p = {x, y};
     Point a = tri->p1;
     Point b = tri->p2;
     Point c = tri->p3;
 
     int as_x = p.x - a.x;
     int as_y = p.y - a.y;
     int s_ab = (b.x - a.x) * as_y - (b.y - a.y) * as_x > 0;
 
     if ((c.x - a.x) * as_y - (c.y - a.y) * as_x > 0 == s_ab) return 0;
     if ((c.x - b.x) * (p.y - b.y) - (c.y - b.y) * (p.x - b.x) > 0 != s_ab) return 0;
 
     return 1;
 }
 
 void renderCircle(GraphicComponent* component, int*** image) {
     Circle* circle = (Circle*)component->data;
     // Get width and height from passed image (more robust than assuming defaults)
     int width = DEFAULT_WIDTH;   // Will be replaced by VM width
     int height = DEFAULT_HEIGHT; // Will be replaced by VM height
 
     for (int y = 0; y < height; y++) {
         for (int x = 0; x < width; x++) {
             if (isInCircle(x, y, circle)) {
                 image[y][x][0] = circle->color.r;
                 image[y][x][1] = circle->color.g;
                 image[y][x][2] = circle->color.b;
             }
         }
     }
 }
 
 void renderRectangle(GraphicComponent* component, int*** image) {
     Rectangle* rect = (Rectangle*)component->data;
     int width = DEFAULT_WIDTH;
     int height = DEFAULT_HEIGHT;
 
     for (int y = 0; y < height; y++) {
         for (int x = 0; x < width; x++) {
             if (isInRectangle(x, y, rect)) {
                 image[y][x][0] = rect->color.r;
                 image[y][x][1] = rect->color.g;
                 image[y][x][2] = rect->color.b;
             }
         }
     }
 }
 
 void renderTriangle(GraphicComponent* component, int*** image) {
     Triangle* tri = (Triangle*)component->data;
     int width = DEFAULT_WIDTH;
     int height = DEFAULT_HEIGHT;
 
     for (int y = 0; y < height; y++) {
         for (int x = 0; x < width; x++) {
             if (isInTriangle(x, y, tri)) {
                 image[y][x][0] = tri->color.r;
                 image[y][x][1] = tri->color.g;
                 image[y][x][2] = tri->color.b;
             }
         }
     }
 }
 
 void renderComposite(GraphicComponent* component, int*** image) {
     CompositeGroup* group = (CompositeGroup*)component->data;
 
     // render all children
     for (int i = 0; i < group->childCount; i++) {
         group->children[i]->render(group->children[i], image);
     }
 }
 

 void freeCircle(GraphicComponent* component) {
     trackedFree(component->data);
     trackedFree(component->name);
     trackedFree(component);
 }
 
 void freeRectangle(GraphicComponent* component) {
     trackedFree(component->data);
     trackedFree(component->name);
     trackedFree(component);
 }
 
 void freeTriangle(GraphicComponent* component) {
     trackedFree(component->data);
     trackedFree(component->name);
     trackedFree(component);
 }
 
 void freeComposite(GraphicComponent* component) {
     CompositeGroup* group = (CompositeGroup*)component->data;
 
     // free children
     for (int i = 0; i < group->childCount; i++) {
         group->children[i]->free(group->children[i]);
     }
 
     trackedFree(group->children);
     trackedFree(group);
     trackedFree(component->name);
     trackedFree(component);
 }
 
 // Factory functions
 GraphicComponent* createCircle(char* name, int centerX, int centerY, int radius, Color color) {
     GraphicComponent* component = (GraphicComponent*)trackedMalloc(sizeof(GraphicComponent), "Circle component");
     if (!component) return NULL;
     
     Circle* circle = (Circle*)trackedMalloc(sizeof(Circle), "Circle data");
     if (!circle) {
         trackedFree(component);
         return NULL;
     }
 
     circle->center.x = centerX;
     circle->center.y = centerY;
     circle->radius = radius;
     circle->color = color;
 
     component->name = strdup(name);
     if (!component->name) {
         trackedFree(circle);
         trackedFree(component);
         return NULL;
     }
     
     component->render = renderCircle;
     component->free = freeCircle;
     component->data = circle;
 
     return component;
 }
 
 GraphicComponent* createRectangle(char* name, int x, int y, int width, int height, Color color) {
     GraphicComponent* component = (GraphicComponent*)trackedMalloc(sizeof(GraphicComponent), "Rectangle component");
     if (!component) return NULL;
     
     Rectangle* rect = (Rectangle*)trackedMalloc(sizeof(Rectangle), "Rectangle data");
     if (!rect) {
         trackedFree(component);
         return NULL;
     }
 
     rect->topLeft.x = x;
     rect->topLeft.y = y;
     rect->width = width;
     rect->height = height;
     rect->color = color;
 
     component->name = strdup(name);
     if (!component->name) {
         trackedFree(rect);
         trackedFree(component);
         return NULL;
     }
     
     component->render = renderRectangle;
     component->free = freeRectangle;
     component->data = rect;
 
     return component;
 }
 
 GraphicComponent* createTriangle(char* name, int x1, int y1, int x2, int y2, int x3, int y3, Color color) {
     GraphicComponent* component = (GraphicComponent*)trackedMalloc(sizeof(GraphicComponent), "Triangle component");
     if (!component) return NULL;
     
     Triangle* tri = (Triangle*)trackedMalloc(sizeof(Triangle), "Triangle data");
     if (!tri) {
         trackedFree(component);
         return NULL;
     }
 
     tri->p1.x = x1;
     tri->p1.y = y1;
     tri->p2.x = x2;
     tri->p2.y = y2;
     tri->p3.x = x3;
     tri->p3.y = y3;
     tri->color = color;
 
     component->name = strdup(name);
     if (!component->name) {
         trackedFree(tri);
         trackedFree(component);
         return NULL;
     }
     
     component->render = renderTriangle;
     component->free = freeTriangle;
     component->data = tri;
 
     return component;
 }
 
 GraphicComponent* createCompositeGroup(char* name) {
     GraphicComponent* component = (GraphicComponent*)trackedMalloc(sizeof(GraphicComponent), "Group component");
     if (!component) return NULL;
     
     CompositeGroup* group = (CompositeGroup*)trackedMalloc(sizeof(CompositeGroup), "Group data");
     if (!group) {
         trackedFree(component);
         return NULL;
     }
 
     // init with default capacity
     group->capacity = INITIAL_CAPACITY;
     group->childCount = 0;
     group->children = (GraphicComponent**)trackedMalloc(
         group->capacity * sizeof(GraphicComponent*),
         "Group children array"
     );
     
     if (!group->children) {
         trackedFree(group);
         trackedFree(component);
         return NULL;
     }
 
     component->name = strdup(name);
     if (!component->name) {
         trackedFree(group->children);
         trackedFree(group);
         trackedFree(component);
         return NULL;
     }
     
     component->render = renderComposite;
     component->free = freeComposite;
     component->data = group;
 
     return component;
 }
 
 // add a child to a composite group
 bool addToGroup(GraphicComponent* group, GraphicComponent* child) {
     if (!group || !child) return false;
     
     CompositeGroup* compositeGroup = (CompositeGroup*)group->data;
 
     // resize if needed
     if (compositeGroup->childCount >= compositeGroup->capacity) {
         int newCapacity = compositeGroup->capacity * 2;
         GraphicComponent** newChildren = (GraphicComponent**)realloc(
             compositeGroup->children,
             newCapacity * sizeof(GraphicComponent*)
         );
         
         if (!newChildren) {
             fprintf(stderr, "Failed to resize group children array\n");
             return false;
         }
         
         compositeGroup->children = newChildren;
         compositeGroup->capacity = newCapacity;
     }
 
     compositeGroup->children[compositeGroup->childCount++] = child;
     return true;
 }
 
 // AST Functions
 ASTNode* createASTNode(NodeType type) {
     ASTNode* node = (ASTNode*)trackedMalloc(sizeof(ASTNode), "AST Node");
     if (!node) return NULL;
     
     node->type = type;
     node->params = NULL;
     node->paramCount = 0;
     node->next = NULL;
     
     return node;
 }
 
 void freeASTNode(ASTNode* node) {
     if (!node) return;
     
     // free parameter strings
     if (node->params) {
         for (int i = 0; i < node->paramCount; i++) {
             if (node->params[i]) {
                 trackedFree(node->params[i]);
             }
         }
         trackedFree(node->params);
     }
     
     trackedFree(node);
 }
 
 void freeAST(ScriptAST* ast) {
     if (!ast) return;
     
     ASTNode* current = ast->head;
     while (current) {
         ASTNode* next = current->next;
         freeASTNode(current);
         current = next;
     }
     
     trackedFree(ast);
 }
 
 bool addNodeToAST(ScriptAST* ast, ASTNode* node) {
     if (!ast || !node) return false;
     
     if (!ast->head) {
         ast->head = node;
         ast->tail = node;
     } else {
         ast->tail->next = node;
         ast->tail = node;
     }
     
     ast->nodeCount++;
     return true;
 }
 
 bool addParamToNode(ASTNode* node, const char* param) {
     if (!node || !param) return false;
     
     // allocate or resize parameter array
     if (node->params == NULL) {
         node->params = (char**)trackedMalloc(sizeof(char*), "AST Node params");
         if (!node->params) return false;
         node->paramCount = 0;
     } else {
         char** newParams = (char**)realloc(
             node->params,
             (node->paramCount + 1) * sizeof(char*)
         );
         
         if (!newParams) return false;
         node->params = newParams;
     }
     
     // add new parameter
     node->params[node->paramCount] = strdup(param);
     if (!node->params[node->paramCount]) return false;
     
     node->paramCount++;
     return true;
 }
 
 // init VM with dynamic arrays
 VM* initVM(int width, int height) {
     VM* vm = (VM*)trackedMalloc(sizeof(VM), "VM");
     if (!vm) return NULL;
     
     vm->width = width;
     vm->height = height;
     
     // init dynamic arrays
     vm->componentCapacity = INITIAL_CAPACITY;
     vm->componentCount = 0;
     vm->components = (GraphicComponent**)trackedMalloc(
         vm->componentCapacity * sizeof(GraphicComponent*),
         "VM components array"
     );
     
     if (!vm->components) {
         trackedFree(vm);
         return NULL;
     }
     
     vm->groupStackCapacity = INITIAL_CAPACITY;
     vm->groupStackPtr = 0;
     vm->groupStack = (GraphicComponent**)trackedMalloc(
         vm->groupStackCapacity * sizeof(GraphicComponent*),
         "VM group stack"
     );
     
     if (!vm->groupStack) {
         trackedFree(vm->components);
         trackedFree(vm);
         return NULL;
     }
     
     // create the AST
     vm->ast = (ScriptAST*)trackedMalloc(sizeof(ScriptAST), "Script AST");
     if (!vm->ast) {
         trackedFree(vm->groupStack);
         trackedFree(vm->components);
         trackedFree(vm);
         return NULL;
     }
     
     vm->ast->head = NULL;
     vm->ast->tail = NULL;
     vm->ast->nodeCount = 0;
     
     // create the image array
     vm->image = (int***)trackedMalloc(height * sizeof(int**), "Image array");
     if (!vm->image) {
         trackedFree(vm->ast);
         trackedFree(vm->groupStack);
         trackedFree(vm->components);
         trackedFree(vm);
         return NULL;
     }
     
     for (int y = 0; y < height; y++) {
         vm->image[y] = (int**)trackedMalloc(width * sizeof(int*), "Image row");
         if (!vm->image[y]) {
             // free previously allocated rows
             for (int j = 0; j < y; j++) {
                 for (int x = 0; x < width; x++) {
                     trackedFree(vm->image[j][x]);
                 }
                 trackedFree(vm->image[j]);
             }
             trackedFree(vm->image);
             trackedFree(vm->ast);
             trackedFree(vm->groupStack);
             trackedFree(vm->components);
             trackedFree(vm);
             return NULL;
         }
         
         for (int x = 0; x < width; x++) {
             vm->image[y][x] = (int*)trackedMalloc(3 * sizeof(int), "Image pixel");
             if (!vm->image[y][x]) {
                 // free previously allocated pixels
                 for (int i = 0; i < x; i++) {
                     trackedFree(vm->image[y][i]);
                 }
                 for (int j = 0; j < y; j++) {
                     for (int i = 0; i < width; i++) {
                         trackedFree(vm->image[j][i]);
                     }
                     trackedFree(vm->image[j]);
                 }
                 trackedFree(vm->image);
                 trackedFree(vm->ast);
                 trackedFree(vm->groupStack);
                 trackedFree(vm->components);
                 trackedFree(vm);
                 return NULL;
             }
             
             // init to (background) white
             vm->image[y][x][0] = 255;
             vm->image[y][x][1] = 255;
             vm->image[y][x][2] = 255;
         }
     }
     
     return vm;
 }
 
 // resize components array
 bool resizeComponentsArray(VM* vm) {
     if (!vm) return false;
     
     int newCapacity = vm->componentCapacity * 2;
     GraphicComponent** newComponents = (GraphicComponent**)realloc(
         vm->components,
         newCapacity * sizeof(GraphicComponent*)
     );
     
     if (!newComponents) {
         fprintf(stderr, "Failed to resize components array\n");
         return false;
     }
     
     vm->components = newComponents;
     vm->componentCapacity = newCapacity;
     return true;
 }
 
 // resize group stack
 bool resizeGroupStack(VM* vm) {
     if (!vm) return false;
     
     int newCapacity = vm->groupStackCapacity * 2;
     GraphicComponent** newStack = (GraphicComponent**)realloc(
         vm->groupStack,
         newCapacity * sizeof(GraphicComponent*)
     );
     
     if (!newStack) {
         fprintf(stderr, "Failed to resize group stack\n");
         return false;
     }
     
     vm->groupStack = newStack;
     vm->groupStackCapacity = newCapacity;
     return true;
 }
 
 // add component to VM
 bool addComponentToVM(VM* vm, GraphicComponent* component) {
     if (!vm || !component) return false;
     
     // resize if needed
     if (vm->componentCount >= vm->componentCapacity) {
         if (!resizeComponentsArray(vm)) {
             return false;
         }
     }
     
     vm->components[vm->componentCount++] = component;
     return true;
 }
 
 // free VM
 void freeVM(VM* vm) {
     if (!vm) return;
     
     // free all components
     for (int i = 0; i < vm->componentCount; i++) {
         // check if this component is a root (not part of any group)
         int isRoot = 1;
         for (int j = 0; j < vm->componentCount; j++) {
             if (vm->components[j]->render == renderComposite) {
                 CompositeGroup* group = (CompositeGroup*)vm->components[j]->data;
                 for (int k = 0; k < group->childCount; k++) {
                     if (group->children[k] == vm->components[i]) {
                         isRoot = 0;
                         break;
                     }
                 }
                 if (!isRoot) break;
             }
         }
         
         // only free root components (groups will free their children)
         if (isRoot) {
             vm->components[i]->free(vm->components[i]);
             // no need to trackedFree here, as component->free already handles this
         }
     }
     
     // free the image array
     if (vm->image) {
         for (int y = 0; y < vm->height; y++) {
             if (vm->image[y]) {
                 for (int x = 0; x < vm->width; x++) {
                     if (vm->image[y][x]) {
                         trackedFree(vm->image[y][x]);
                     }
                 }
                 trackedFree(vm->image[y]);
             }
         }
         trackedFree(vm->image);
     }
     
     // free the AST
     freeAST(vm->ast);
     
     // free component array and group stack
     trackedFree(vm->components);
     trackedFree(vm->groupStack);
     
     trackedFree(vm);
 }
 
 // parse a color from a string (formats: "r,g,b" or named colors)
 Color parseColor(const char* colorStr) {
     Color color = {0, 0, 0}; // default black
     
     // check for named colors
     if (strcmp(colorStr, "red") == 0) {
         color.r = 255; color.g = 0; color.b = 0;
     } else if (strcmp(colorStr, "green") == 0) {
         color.r = 0; color.g = 255; color.b = 0;
     } else if (strcmp(colorStr, "blue") == 0) {
         color.r = 0; color.g = 0; color.b = 255;
     } else if (strcmp(colorStr, "yellow") == 0) {
         color.r = 255; color.g = 255; color.b = 0;
     } else if (strcmp(colorStr, "cyan") == 0) {
         color.r = 0; color.g = 255; color.b = 255;
     } else if (strcmp(colorStr, "magenta") == 0) {
         color.r = 255; color.g = 0; color.b = 255;
     } else if (strcmp(colorStr, "white") == 0) {
         color.r = 255; color.g = 255; color.b = 255;
     } else if (strcmp(colorStr, "black") == 0) {
         color.r = 0; color.g = 0; color.b = 0;
     } else {
         // try parsing as "r,g,b"
         sscanf(colorStr, "%d,%d,%d", &color.r, &color.g, &color.b);
         
         // clamp values
         color.r = (color.r < 0) ? 0 : (color.r > 255 ? 255 : color.r);
         color.g = (color.g < 0) ? 0 : (color.g > 255 ? 255 : color.g);
         color.b = (color.b < 0) ? 0 : (color.b > 255 ? 255 : color.b);
     }
     
     return color;
 }
 
 // split a line into tokens
 int tokenize(char* line, char* tokens[], int maxTokens) {
     int count = 0;
     char* token = strtok(line, " \t\n");
     
     while (token != NULL && count < maxTokens) {
         tokens[count++] = token;
         token = strtok(NULL, " \t\n");
     }
     
     return count;
 }
 
 // find a component by name
 GraphicComponent* findComponent(VM* vm, const char* name) {
     for (int i = 0; i < vm->componentCount; i++) {
         if (strcmp(vm->components[i]->name, name) == 0) {
             return vm->components[i];
         }
     }
     return NULL;
 }
 
 // parse a script into an AST
 bool parseScript(VM* vm, const char* script) {
     if (!vm || !script) return false;
     
     char line[MAX_LINE_LENGTH];
     const char* ptr = script;
     int linePos = 0;
     
     while (*ptr) {
         if (*ptr == '\n' || *ptr == '\0') {
             line[linePos] = '\0';
             
             // skip empty lines and comments
             if (linePos > 0 && line[0] != '/' && line[0] != '#') {
                 char lineCopy[MAX_LINE_LENGTH];
                 strncpy(lineCopy, line, MAX_LINE_LENGTH);
                 lineCopy[MAX_LINE_LENGTH-1] = '\0'; // null termination
                 
                 char* tokens[MAX_TOKENS];
                 int tokenCount = tokenize(lineCopy, tokens, MAX_TOKENS);
                 
                 if (tokenCount > 0) {
                     ASTNode* node = NULL;
                     
                     // determine node type based on command
                     if (strcmp(tokens[0], "canvas") == 0) {
                         node = createASTNode(NODE_CANVAS);
                     } else if (strcmp(tokens[0], "circle") == 0) {
                         node = createASTNode(NODE_CIRCLE);
                     } else if (strcmp(tokens[0], "rectangle") == 0 || strcmp(tokens[0], "rect") == 0) {
                         node = createASTNode(NODE_RECTANGLE);
                     } else if (strcmp(tokens[0], "triangle") == 0) {
                         node = createASTNode(NODE_TRIANGLE);
                     } else if (strcmp(tokens[0], "group") == 0) {
                         node = createASTNode(NODE_GROUP_START);
                     } else if (strcmp(tokens[0], "end") == 0) {
                         node = createASTNode(NODE_GROUP_END);
                     } else if (strcmp(tokens[0], "render") == 0) {
                         node = createASTNode(NODE_RENDER);
                     }
                     
                     if (node) {
                         // add all tokens as parameters
                         for (int i = 0; i < tokenCount; i++) {
                             if (!addParamToNode(node, tokens[i])) {
                                 freeASTNode(node);
                                 fprintf(stderr, "Failed to add parameter to AST node\n");
                                 return false;
                             }
                         }
                         
                         // add node to AST
                         if (!addNodeToAST(vm->ast, node)) {
                             freeASTNode(node);
                             fprintf(stderr, "Failed to add node to AST\n");
                             return false;
                         }
                     }
                 }
             }
             
             linePos = 0;
         } else {
             if (linePos < MAX_LINE_LENGTH - 1) {
                 line[linePos++] = *ptr;
             }
         }
         
         ptr++;
         if (*ptr == '\0' && linePos > 0) {
             // handle the last line if it doesn't end with newline
             ptr--; // revisit this character
         }
     }
     
     return true;
 }
 
 // execute AST
 bool executeAST(VM* vm) {
     if (!vm || !vm->ast) return false;
     
     ASTNode* current = vm->ast->head;
     while (current) {
         switch (current->type) {
             case NODE_CANVAS: {
                 if (current->paramCount >= 3) {
                     int width = atoi(current->params[1]);
                     int height = atoi(current->params[2]);
                     
                     // update VM dimensions if needed
                     if (width > 0 && height > 0 && 
                         (width != vm->width || height != vm->height)) {
                         // re-init the image with new dimensions
                         // (in a real implementation, we would resize here!)
                         fprintf(stderr, "Warning: Canvas resize not implemented, using initial size\n");
                     }
                 }
                 break;
             }
             
             case NODE_CIRCLE: {
                 if (current->paramCount >= 6) {
                     char* name = current->params[1];
                     int centerX = atoi(current->params[2]);
                     int centerY = atoi(current->params[3]);
                     int radius = atoi(current->params[4]);
                     Color color = parseColor(current->params[5]);
                     
                     GraphicComponent* circle = createCircle(name, centerX, centerY, radius, color);
                     if (circle) {
                         // add to current group or VM root
                         if (vm->groupStackPtr > 0) {
                             GraphicComponent* group = vm->groupStack[vm->groupStackPtr - 1];
                             if (!addToGroup(group, circle)) {
                                 fprintf(stderr, "Failed to add circle to group\n");
                                 circle->free(circle);
                                 return false;
                             }
                         } else {
                             if (!addComponentToVM(vm, circle)) {
                                 fprintf(stderr, "Failed to add circle to VM\n");
                                 circle->free(circle);
                                 return false;
                             }
                         }
                     } else {
                         fprintf(stderr, "Failed to create circle\n");
                         return false;
                     }
                 }
                 break;
             }
             
             case NODE_RECTANGLE: {
                 if (current->paramCount >= 7) {
                     char* name = current->params[1];
                     int x = atoi(current->params[2]);
                     int y = atoi(current->params[3]);
                     int width = atoi(current->params[4]);
                     int height = atoi(current->params[5]);
                     Color color = parseColor(current->params[6]);
                     
                     GraphicComponent* rect = createRectangle(name, x, y, width, height, color);
                     if (rect) {
                         // add to current group or VM root
                         if (vm->groupStackPtr > 0) {
                             GraphicComponent* group = vm->groupStack[vm->groupStackPtr - 1];
                             if (!addToGroup(group, rect)) {
                                 fprintf(stderr, "Failed to add rectangle to group\n");
                                 rect->free(rect);
                                 return false;
                             }
                         } else {
                             if (!addComponentToVM(vm, rect)) {
                                 fprintf(stderr, "Failed to add rectangle to VM\n");
                                 rect->free(rect);
                                 return false;
                             }
                         }
                     } else {
                         fprintf(stderr, "Failed to create rectangle\n");
                         return false;
                     }
                 }
                 break;
             }
             
             case NODE_TRIANGLE: {
                 if (current->paramCount >= 9) {
                     char* name = current->params[1];
                     int x1 = atoi(current->params[2]);
                     int y1 = atoi(current->params[3]);
                     int x2 = atoi(current->params[4]);
                     int y2 = atoi(current->params[5]);
                     int x3 = atoi(current->params[6]);
                     int y3 = atoi(current->params[7]);
                     Color color = parseColor(current->params[8]);
                     
                     GraphicComponent* triangle = createTriangle(name, x1, y1, x2, y2, x3, y3, color);
                     if (triangle) {
                         // add to current group or VM root
                         if (vm->groupStackPtr > 0) {
                             GraphicComponent* group = vm->groupStack[vm->groupStackPtr - 1];
                             if (!addToGroup(group, triangle)) {
                                 fprintf(stderr, "Failed to add triangle to group\n");
                                 triangle->free(triangle);
                                 return false;
                             }
                         } else {
                             if (!addComponentToVM(vm, triangle)) {
                                 fprintf(stderr, "Failed to add triangle to VM\n");
                                 triangle->free(triangle);
                                 return false;
                             }
                         }
                     } else {
                         fprintf(stderr, "Failed to create triangle\n");
                         return false;
                     }
                 }
                 break;
             }
             
             case NODE_GROUP_START: {
                 if (current->paramCount >= 2) {
                     char* name = current->params[1];
                     
                     GraphicComponent* group = createCompositeGroup(name);
                     if (group) {
                         // add to current group or VM root
                         if (vm->groupStackPtr > 0) {
                             GraphicComponent* parentGroup = vm->groupStack[vm->groupStackPtr - 1];
                             if (!addToGroup(parentGroup, group)) {
                                 fprintf(stderr, "Failed to add group to parent group\n");
                                 group->free(group);
                                 return false;
                             }
                         } else {
                             if (!addComponentToVM(vm, group)) {
                                 fprintf(stderr, "Failed to add group to VM\n");
                                 group->free(group);
                                 return false;
                             }
                         }
                         
                         // push to stack
                         if (vm->groupStackPtr >= vm->groupStackCapacity) {
                             if (!resizeGroupStack(vm)) {
                                 fprintf(stderr, "Failed to resize group stack\n");
                                 return false;
                             }
                         }
                         
                         vm->groupStack[vm->groupStackPtr++] = group;
                     } else {
                         fprintf(stderr, "Failed to create group\n");
                         return false;
                     }
                 }
                 break;
             }
             
             case NODE_GROUP_END: {
                 if (vm->groupStackPtr > 0) {
                     vm->groupStackPtr--;
                 } else {
                     fprintf(stderr, "Warning: Unmatched group end\n");
                 }
                 break;
             }
             
             case NODE_RENDER: {
                 // render all top-level components
                 for (int i = 0; i < vm->componentCount; i++) {
                     // only render components that are roots (not part of any group)
                     // groups will render their children
                     int isRoot = 1;
                     for (int j = 0; j < vm->componentCount; j++) {
                         if (vm->components[j]->render == renderComposite) {
                             CompositeGroup* group = (CompositeGroup*)vm->components[j]->data;
                             for (int k = 0; k < group->childCount; k++) {
                                 if (group->children[k] == vm->components[i]) {
                                     isRoot = 0;
                                     break;
                                 }
                             }
                             if (!isRoot) break;
                         }
                     }
                     
                     if (isRoot) {
                         vm->components[i]->render(vm->components[i], vm->image);
                     }
                 }
                 break;
             }
         }
         
         current = current->next;
     }
     
     return true;
 }
 
 // output to PPM file
 bool outputImage(VM* vm, const char* filename) {
     if (!vm || !filename) return false;
     
     FILE* file = fopen(filename, "wb");
     if (!file) {
         fprintf(stderr, "Failed to open output file: %s\n", filename);
         return false;
     }
     
     // PPM header
     fprintf(file, "P3\n%d %d\n%d\n", vm->width, vm->height, MAX_COLOR);
     
     // pixel data
     for (int y = 0; y < vm->height; y++) {
         for (int x = 0; x < vm->width; x++) {
             fprintf(file, "%d %d %d ", 
                 vm->image[y][x][0], 
                 vm->image[y][x][1], 
                 vm->image[y][x][2]);
         }
         fprintf(file, "\n");
     }
     
     fclose(file);
     return true;
 }
 
 // parse and execute a script file
 bool processScriptFile(const char* filename, int width, int height, const char* outputFilename) {
     FILE* file = fopen(filename, "rb");
     if (!file) {
         fprintf(stderr, "Failed to open script file: %s\n", filename);
         return false;
     }
     
     // get file size first
     fseek(file, 0, SEEK_END);
     long fileSize = ftell(file);
     rewind(file);
     
     // check file size
     if (fileSize <= 0 || fileSize > MAX_SCRIPT_SIZE) {
         fprintf(stderr, "Invalid script file size: %ld\n", fileSize);
         fclose(file);
         return false;
     }
     
     // allocate memory for script content
     char* script = (char*)trackedMalloc(fileSize + 1, "Script content");
     if (!script) {
         fprintf(stderr, "Failed to allocate memory for script\n");
         fclose(file);
         return false;
     }
     
     // read script content
     size_t bytesRead = fread(script, 1, fileSize, file);
     fclose(file);
     
     if (bytesRead != (size_t)fileSize) {
         fprintf(stderr, "Failed to read entire script file\n");
         trackedFree(script);
         return false;
     }
     
     // null-terminate script
     script[fileSize] = '\0';
     
     // init VM
     VM* vm = initVM(width, height);
     if (!vm) {
         fprintf(stderr, "Failed to initialize VM\n");
         trackedFree(script);
         return false;
     }
     
     // parse script into AST
     if (!parseScript(vm, script)) {
         fprintf(stderr, "Failed to parse script\n");
         freeVM(vm);
         trackedFree(script);
         return false;
     }
     
     // execute AST
     if (!executeAST(vm)) {
         fprintf(stderr, "Failed to execute script\n");
         freeVM(vm);
         trackedFree(script);
         return false;
     }
     
     // output image
     if (!outputImage(vm, outputFilename)) {
         fprintf(stderr, "Failed to output image\n");
         freeVM(vm);
         trackedFree(script);
         return false;
     }
     
     // clean
     freeVM(vm);
     trackedFree(script);
     
     printf("Successfully processed script and generated image: %s\n", outputFilename);
     printMemoryStats();
     
     return true;
 }
 
 // usage
 void printUsage(const char* programName) {
     printf("Usage: %s <script_file> [width] [height] [output_file]\n", programName);
     printf("  script_file: Path to graphics script file\n");
     printf("  width: Image width (default: %d)\n", DEFAULT_WIDTH);
     printf("  height: Image height (default: %d)\n", DEFAULT_HEIGHT);
     printf("  output_file: Output image file path (default: output.ppm)\n");
 }
 

 int main(int argc, char* argv[]) {
     if (argc < 2) {
         printUsage(argv[0]);
         return 1;
     }
     
     const char* scriptFile = argv[1];
     int width = (argc > 2) ? atoi(argv[2]) : DEFAULT_WIDTH;
     int height = (argc > 3) ? atoi(argv[3]) : DEFAULT_HEIGHT;
     const char* outputFile = (argc > 4) ? argv[4] : "output.ppm";
     
     // validate width and height
     if (width <= 0 || height <= 0) {
         fprintf(stderr, "Invalid dimensions: width and height must be positive\n");
         return 1;
     }
     
     bool success = processScriptFile(scriptFile, width, height, outputFile);
     
     return success ? 0 : 1;
 }