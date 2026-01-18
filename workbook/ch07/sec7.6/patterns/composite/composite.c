// C++ standard library version: This project uses the C17 standard library version.
/* This example implements a simple graphics system where shapes can be
 * composed into groups, and both individual shapes and groups can be
 * rendered to a PPM (P3) image file.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define WIDTH 400
#define HEIGHT 400
#define MAX_COLOR 255

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

// Utils
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

    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
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

    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
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

    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
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
    free(component->data);
    free(component->name);
    free(component);
}

void freeRectangle(GraphicComponent* component) {
    free(component->data);
    free(component->name);
    free(component);
}

void freeTriangle(GraphicComponent* component) {
    free(component->data);
    free(component->name);
    free(component);
}

void freeComposite(GraphicComponent* component) {
    CompositeGroup* group = (CompositeGroup*)component->data;

    // free children
    for (int i = 0; i < group->childCount; i++) {
        group->children[i]->free(group->children[i]);
    }

    free(group->children);
    free(group);
    free(component->name);
    free(component);
}

// Factory functions
GraphicComponent* createCircle(char* name, int centerX, int centerY, int radius, Color color) {
    GraphicComponent* component = (GraphicComponent*)malloc(sizeof(GraphicComponent));
    Circle* circle = (Circle*)malloc(sizeof(Circle));

    circle->center.x = centerX;
    circle->center.y = centerY;
    circle->radius = radius;
    circle->color = color;

    component->name = strdup(name);
    component->render = renderCircle;
    component->free = freeCircle;
    component->data = circle;

    return component;
}

GraphicComponent* createRectangle(char* name, int x, int y, int width, int height, Color color) {
    GraphicComponent* component = (GraphicComponent*)malloc(sizeof(GraphicComponent));
    Rectangle* rect = (Rectangle*)malloc(sizeof(Rectangle));

    rect->topLeft.x = x;
    rect->topLeft.y = y;
    rect->width = width;
    rect->height = height;
    rect->color = color;

    component->name = strdup(name);
    component->render = renderRectangle;
    component->free = freeRectangle;
    component->data = rect;

    return component;
}

GraphicComponent* createTriangle(char* name, int x1, int y1, int x2, int y2, int x3, int y3, Color color) {
    GraphicComponent* component = (GraphicComponent*)malloc(sizeof(GraphicComponent));
    Triangle* tri = (Triangle*)malloc(sizeof(Triangle));

    tri->p1.x = x1;
    tri->p1.y = y1;
    tri->p2.x = x2;
    tri->p2.y = y2;
    tri->p3.x = x3;
    tri->p3.y = y3;
    tri->color = color;

    component->name = strdup(name);
    component->render = renderTriangle;
    component->free = freeTriangle;
    component->data = tri;

    return component;
}

GraphicComponent* createCompositeGroup(char* name) {
    GraphicComponent* component = (GraphicComponent*)malloc(sizeof(GraphicComponent));
    CompositeGroup* group = (CompositeGroup*)malloc(sizeof(CompositeGroup));

    // init with capacity for 15 children
    group->capacity = 15;
    group->childCount = 0;
    group->children = (GraphicComponent**)malloc(group->capacity * sizeof(GraphicComponent*));

    component->name = strdup(name);
    component->render = renderComposite;
    component->free = freeComposite;
    component->data = group;

    return component;
}

// add a child to a composite group
void addToGroup(GraphicComponent* group, GraphicComponent* child) {
    CompositeGroup* compositeGroup = (CompositeGroup*)group->data;

    // Resize if needed
    if (compositeGroup->childCount >= compositeGroup->capacity) {
        compositeGroup->capacity *= 2;
        compositeGroup->children = (GraphicComponent**)realloc(
            compositeGroup->children,
            compositeGroup->capacity * sizeof(GraphicComponent*)
        );
    }

    compositeGroup->children[compositeGroup->childCount++] = child;
}


void savePPM(int*** image, const char* filename) {
    FILE* file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "Error opening file for writing: %s\n", filename);
        return;
    }

    // write PPM header
    fprintf(file, "P3\n");
    fprintf(file, "%d %d\n", WIDTH, HEIGHT);
    fprintf(file, "%d\n", MAX_COLOR);

    // write pixel data
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            fprintf(file, "%d %d %d ", image[y][x][0], image[y][x][1], image[y][x][2]);
        }
        fprintf(file, "\n");
    }

    fclose(file);
    printf("Image saved to %s\n", filename);
}


int main() {

    int*** image = (int***)malloc(HEIGHT * sizeof(int**));
    for (int y = 0; y < HEIGHT; y++) {
        image[y] = (int**)malloc(WIDTH * sizeof(int*));
        for (int x = 0; x < WIDTH; x++) {
            image[y][x] = (int*)malloc(3 * sizeof(int));
            image[y][x][0] = 255; // white for init
            image[y][x][1] = 255;
            image[y][x][2] = 255;
        }
    }

    GraphicComponent* lightBlueRectangle = createRectangle("Öight Blue Rectangle", 0, 0, 400, 400, (Color){128, 128, 255});
    GraphicComponent* redCircle = createCircle("Yellow Circle", 100, 100, 50, (Color){255, 255, 0});
    GraphicComponent* greenRectangle = createRectangle("Green Rectangle", 0, 300, 400, 100, (Color){20, 128, 20});
    GraphicComponent* greenTriangle = createTriangle(
        "Green Triangle",
        350, 300,  // p1
        40, 400,   // p2
        300, 400,  // p3
        (Color){0, 255, 0}
    );

    // Create a composite group for a house (composite of shapes)
    GraphicComponent* house = createCompositeGroup("House");

    // House base (rectangle)
    GraphicComponent* houseBase = createRectangle("House Base", 150, 250, 100, 80, (Color){150, 75, 0});

    // House roof (triangle)
    GraphicComponent* houseRoof = createTriangle(
        "House Roof",
        150, 250,  // bottom left
        250, 250,  // bottom right
        200, 200,  // top
        (Color){255, 0, 0}
    );

    // House door (rectangle)
    GraphicComponent* houseDoor = createRectangle("House Door", 180, 290, 30, 40, (Color){70, 40, 0});

    // Add parts to the house
    addToGroup(house, houseBase);
    addToGroup(house, houseRoof);
    addToGroup(house, houseDoor);

    // Create a scene (composite of shapes and composites)
    GraphicComponent* scene = createCompositeGroup("Scene");
    addToGroup(scene, lightBlueRectangle); // Background
    addToGroup(scene, redCircle);          // Sun
    addToGroup(scene, greenRectangle);     // Ground
    addToGroup(scene, greenTriangle);      // Road
    addToGroup(scene, house);              // House (which is itself a composite)

    // Render the entire scene
    scene->render(scene, image);

    // Save the image
    savePPM(image, "composite_pattern.ppm");

    // Free everything
    scene->free(scene);

    // Free the image array
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            free(image[y][x]);
        }
        free(image[y]);
    }
    free(image);

    return 0;
}
