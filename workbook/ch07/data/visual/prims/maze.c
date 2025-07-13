#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <math.h>

#ifdef NCURSES_AVAILABLE
#include <ncurses.h>
#define USE_NCURSES 1
#else
#define USE_NCURSES 0
#endif

#define MAX_ROOMS 15
#define MAX_CORRIDORS 30
#define MAX_CONNECTIONS 4
#define GRID_WIDTH 80
#define GRID_HEIGHT 25
#define MIN_ROOM_SIZE 3
#define MAX_ROOM_SIZE 6
#define MIN_ROOM_DISTANCE 8
#define MAX_PLACEMENT_ATTEMPTS 50
#define ANIMATION_DELAY 200000 // microseconds

typedef struct {
    int x, y;
} Point;

typedef struct {
    Point position;
    int width, height;
    int id;
    int visit_count;
    time_t last_visit;
} Room;

typedef struct {
    int from_room;
    int to_room;
    Point *path;
    int path_length;
} Corridor;

typedef struct {
    int room_index;
    int visit_count;
    time_t last_visit;
} VisitRecord;

typedef struct {
    Room rooms[MAX_ROOMS];
    Corridor corridors[MAX_CORRIDORS];
    int room_count;
    int corridor_count;
    int connections[MAX_ROOMS][MAX_CONNECTIONS];
    int connection_count[MAX_ROOMS];
    VisitRecord visit_history[MAX_ROOMS];
    int current_room;
    Point player_pos;
    char grid[GRID_HEIGHT][GRID_WIDTH];
} Dungeon;

// Global instance
Dungeon dungeon;

// Utils
double distance(Point a, Point b) {
    return sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
}

int random_range(int min, int max) {
    return min + rand() % (max - min + 1);
}

// room gen
int is_valid_room_position(Point pos, int width, int height) {
    // check bounds
    if (pos.x - width/2 < 1 || pos.x + width/2 >= GRID_WIDTH - 1 ||
        pos.y - height/2 < 1 || pos.y + height/2 >= GRID_HEIGHT - 1) {
        return 0;
    }
    
    // check distance from existing rooms
    for (int i = 0; i < dungeon.room_count; i++) {
        double dist = distance(pos, dungeon.rooms[i].position);
        if (dist < MIN_ROOM_DISTANCE) {
            return 0;
        }
    }
    
    return 1;
}

void generate_rooms() {
    dungeon.room_count = 0;
    
    for (int i = 0; i < MAX_ROOMS; i++) {
        int attempts = 0;
        Point pos;
        int width = random_range(MIN_ROOM_SIZE, MAX_ROOM_SIZE);
        int height = random_range(MIN_ROOM_SIZE, MAX_ROOM_SIZE);
        
        while (attempts < MAX_PLACEMENT_ATTEMPTS) {
            pos.x = random_range(width/2 + 2, GRID_WIDTH - width/2 - 2);
            pos.y = random_range(height/2 + 2, GRID_HEIGHT - height/2 - 2);
            
            if (is_valid_room_position(pos, width, height)) {
                Room *room = &dungeon.rooms[dungeon.room_count];
                room->position = pos;
                room->width = width;
                room->height = height;
                room->id = dungeon.room_count + 1;
                room->visit_count = 0;
                room->last_visit = 0;
                
                // Init visit history
                dungeon.visit_history[dungeon.room_count].room_index = dungeon.room_count;
                dungeon.visit_history[dungeon.room_count].visit_count = 0;
                dungeon.visit_history[dungeon.room_count].last_visit = 0;
                
                dungeon.room_count++;
                break;
            }
            attempts++;
        }
    }
}

// Minimum Spanning Tree using Prim's algorithm
void connect_rooms_mst() {
    if (dungeon.room_count < 2) return;
    
    int visited[MAX_ROOMS] = {0};
    int edges[MAX_ROOMS][MAX_ROOMS];
    double weights[MAX_ROOMS][MAX_ROOMS];
    
    // Init connection arrays
    for (int i = 0; i < dungeon.room_count; i++) {
        dungeon.connection_count[i] = 0;
        for (int j = 0; j < MAX_CONNECTIONS; j++) {
            dungeon.connections[i][j] = -1;
        }
    }
    
    // Calc all distances
    for (int i = 0; i < dungeon.room_count; i++) {
        for (int j = 0; j < dungeon.room_count; j++) {
            if (i != j) {
                weights[i][j] = distance(dungeon.rooms[i].position, dungeon.rooms[j].position);
            } else {
                weights[i][j] = 0;
            }
        }
    }
    
    // start with room 0
    visited[0] = 1;
    int visited_count = 1;
    dungeon.corridor_count = 0;
    
    while (visited_count < dungeon.room_count) {
        double min_weight = 1000000;
        int min_from = -1, min_to = -1;
        
        // find minimum weight edge from visited to unvisited
        for (int i = 0; i < dungeon.room_count; i++) {
            if (visited[i]) {
                for (int j = 0; j < dungeon.room_count; j++) {
                    if (!visited[j] && weights[i][j] < min_weight) {
                        min_weight = weights[i][j];
                        min_from = i;
                        min_to = j;
                    }
                }
            }
        }
        
        if (min_from != -1 && min_to != -1) {
            // add connection
            if (dungeon.connection_count[min_from] < MAX_CONNECTIONS) {
                dungeon.connections[min_from][dungeon.connection_count[min_from]] = min_to;
                dungeon.connection_count[min_from]++;
            }
            if (dungeon.connection_count[min_to] < MAX_CONNECTIONS) {
                dungeon.connections[min_to][dungeon.connection_count[min_to]] = min_from;
                dungeon.connection_count[min_to]++;
            }
            
            // create corridor
            Corridor *corridor = &dungeon.corridors[dungeon.corridor_count];
            corridor->from_room = min_from;
            corridor->to_room = min_to;
            corridor->path = NULL;
            corridor->path_length = 0;
            dungeon.corridor_count++;
            
            visited[min_to] = 1;
            visited_count++;
        }
    }
}

// grid rendering
void clear_grid() {
    for (int y = 0; y < GRID_HEIGHT; y++) {
        for (int x = 0; x < GRID_WIDTH; x++) {
            dungeon.grid[y][x] = ' ';
        }
    }
}

void draw_room_to_grid(int room_index) {
    Room *room = &dungeon.rooms[room_index];
    int left = room->position.x - room->width/2;
    int right = room->position.x + room->width/2;
    int top = room->position.y - room->height/2;
    int bottom = room->position.y + room->height/2;
    
    // draw room walls
    for (int y = top; y <= bottom; y++) {
        for (int x = left; x <= right; x++) {
            if (x >= 0 && x < GRID_WIDTH && y >= 0 && y < GRID_HEIGHT) {
                if (x == left || x == right || y == top || y == bottom) {
                    dungeon.grid[y][x] = '#';
                } else {
                    // room interior - show visit status
                    if (room->visit_count == 0) {
                        dungeon.grid[y][x] = '.';  // -- Unvisited
                    } else if (time(NULL) - room->last_visit < 10) {
                        dungeon.grid[y][x] = '!';  // -- Recently visited
                    } else {
                        dungeon.grid[y][x] = 'o';  // -- Visited
                    }
                }
            }
        }
    }
    
    // draw room ID in center
    if (room->position.x >= 0 && room->position.x < GRID_WIDTH && 
        room->position.y >= 0 && room->position.y < GRID_HEIGHT) {
        dungeon.grid[room->position.y][room->position.x] = '0' + (room->id % 10);
    }
}

void draw_corridor_to_grid(int from_room, int to_room) {
    Point start = dungeon.rooms[from_room].position;
    Point end = dungeon.rooms[to_room].position;
    
    // L-shaped corridor
    Point current = start;
    
    // horizontal line first
    int dx = (end.x > start.x) ? 1 : -1;
    while (current.x != end.x) {
        if (current.x >= 0 && current.x < GRID_WIDTH && 
            current.y >= 0 && current.y < GRID_HEIGHT) {
            if (dungeon.grid[current.y][current.x] == ' ') {
                dungeon.grid[current.y][current.x] = '-';
            }
        }
        current.x += dx;
    }
    
    // vertical line
    int dy = (end.y > start.y) ? 1 : -1;
    while (current.y != end.y) {
        if (current.x >= 0 && current.x < GRID_WIDTH && 
            current.y >= 0 && current.y < GRID_HEIGHT) {
            if (dungeon.grid[current.y][current.x] == ' ') {
                dungeon.grid[current.y][current.x] = '|';
            }
        }
        current.y += dy;
    }
}

// simpler impl. above ..
// in draw_corridor_to_grid, we could also use e.g. Bresenham's line algo
// if we wanted a more complex pathfinding, but for now, L-shaped is fine
// and it is was one of the requirements
void generate_corridor_path(Corridor *corridor) {
    // Using: path, and path_length .. in Corridor struct (now not used)
    // Here we could populate corridor->path with actual pathfinding
    // corridor->path = malloc(sizeof(Point) * calculated_length);
    // .. pathfinding algo ..
}

void draw_player_to_grid() {
    if (dungeon.player_pos.x >= 0 && dungeon.player_pos.x < GRID_WIDTH && 
        dungeon.player_pos.y >= 0 && dungeon.player_pos.y < GRID_HEIGHT) {
        dungeon.grid[dungeon.player_pos.y][dungeon.player_pos.x] = '@';
    }
}

void render_grid() {
    clear_grid();
    
    // corridors first
    for (int i = 0; i < dungeon.corridor_count; i++) {
        draw_corridor_to_grid(dungeon.corridors[i].from_room, dungeon.corridors[i].to_room);
    }
    
    // rooms
    for (int i = 0; i < dungeon.room_count; i++) {
        draw_room_to_grid(i);
    }
    
    // and player
    draw_player_to_grid();
}

// fwd decl ..
int count_visited_rooms();

void print_grid() {
    #if USE_NCURSES
    clear();
    for (int y = 0; y < GRID_HEIGHT; y++) {
        for (int x = 0; x < GRID_WIDTH; x++) {
            char c = dungeon.grid[y][x];
            if (c == '@') {
                attron(COLOR_PAIR(1));  // player in red
                mvaddch(y, x, c);
                attroff(COLOR_PAIR(1));
            } else if (c == '!') {
                attron(COLOR_PAIR(2));  // recently visited in yellow
                mvaddch(y, x, c);
                attroff(COLOR_PAIR(2));
            } else if (c >= '0' && c <= '9') {
                attron(COLOR_PAIR(3));  // room numbers in blue
                mvaddch(y, x, c);
                attroff(COLOR_PAIR(3));
            } else {
                mvaddch(y, x, c);
            }
        }
    }
    
    // stats
    mvprintw(GRID_HEIGHT + 1, 0, "Current Room: %d | Rooms Visited: %d/%d", 
             dungeon.current_room + 1, count_visited_rooms(), dungeon.room_count);
    mvprintw(GRID_HEIGHT + 2, 0, "Legend: @ = Player, # = Walls, . = Unvisited, o = Visited, ! = Recent");
    mvprintw(GRID_HEIGHT + 3, 0, "Press 'q' to quit, 'r' to reset, any key to continue");
    
    refresh();
    #else
    system("clear");
    for (int y = 0; y < GRID_HEIGHT; y++) {
        for (int x = 0; x < GRID_WIDTH; x++) {
            putchar(dungeon.grid[y][x]);
        }
        putchar('\n');
    }
    
    printf("\nCurrent Room: %d | Rooms Visited: %d/%d\n", (dungeon.current_room + 1), count_visited_rooms(), dungeon.room_count);
    printf("Legend: @ = Player, # = Walls, . = Unvisited, o = Visited, ! = Recent\n");
    printf("Press Enter to continue, 'q' to quit, 'r' to reset\n");
    #endif
}

// movement and logic
int count_visited_rooms() {
    int count = 0;
    for (int i = 0; i < dungeon.room_count; i++) {
        if (dungeon.rooms[i].visit_count > 0) {
            count++;
        }
    }
    return count;
}

void record_visit(int room_index) {
    dungeon.rooms[room_index].visit_count++;
    dungeon.rooms[room_index].last_visit = time(NULL);
    dungeon.visit_history[room_index].visit_count++;
    dungeon.visit_history[room_index].last_visit = time(NULL);
}

int choose_next_room() {
    if (dungeon.connection_count[dungeon.current_room] == 0) {
        return dungeon.current_room;
    }
    
    // unvisited rooms first
    int unvisited_connections[MAX_CONNECTIONS];
    int unvisited_count = 0;
    
    for (int i = 0; i < dungeon.connection_count[dungeon.current_room]; i++) {
        int room_index = dungeon.connections[dungeon.current_room][i];
        if (dungeon.rooms[room_index].visit_count == 0) {
            unvisited_connections[unvisited_count++] = room_index;
        }
    }
    
    if (unvisited_count > 0) {
        return unvisited_connections[rand() % unvisited_count];
    }
    
    // if all connected rooms are visited, choose least recently visited
    int best_room = dungeon.connections[dungeon.current_room][0];
    time_t oldest_visit = dungeon.rooms[best_room].last_visit;
    
    for (int i = 1; i < dungeon.connection_count[dungeon.current_room]; i++) {
        int room_index = dungeon.connections[dungeon.current_room][i];
        if (dungeon.rooms[room_index].last_visit < oldest_visit) {
            oldest_visit = dungeon.rooms[room_index].last_visit;
            best_room = room_index;
        }
    }
    
    return best_room;
}

void move_to_room(int target_room) {
    dungeon.current_room = target_room;
    dungeon.player_pos = dungeon.rooms[target_room].position;
    record_visit(target_room);
}

void initialize_dungeon() {
    srand(time(NULL));

    generate_rooms();
    connect_rooms_mst();
    
    if (dungeon.room_count > 0) {
        dungeon.current_room = 0; // first room
        dungeon.player_pos = dungeon.rooms[0].position;
        record_visit(0);
    }
}

void reset_dungeon() {
    initialize_dungeon();
}

int main() {
    char input;
    int running = 1;
    
    #if USE_NCURSES
    initscr();
    start_color();
    init_pair(1, COLOR_RED, COLOR_BLACK);     // player
    init_pair(2, COLOR_YELLOW, COLOR_BLACK);  // recent visits
    init_pair(3, COLOR_BLUE, COLOR_BLACK);    // room numbers
    noecho();
    cbreak();
    nodelay(stdscr, TRUE);
    #endif
    
    initialize_dungeon();
    
    printf("Dungeon explorer\n");
    printf("================\n");
    
    #if USE_NCURSES
    printf("Using ncurses for enhanced display!\n");
    #else
    printf("No ncurses - basic ASCII display\n");
    #endif
    
    printf("Generated %d rooms connected by %d corridors\n", dungeon.room_count, dungeon.corridor_count);
    
    #if !USE_NCURSES
    printf("Press Enter to start ..\n");
    getchar();
    #endif
    
    while (running) {
        render_grid();
        print_grid();
        
        #if USE_NCURSES
        usleep(ANIMATION_DELAY);
        input = getch();
        
        if (input == 'q' || input == 'Q') {
            running = 0;
        } else if (input == 'r' || input == 'R') {
            reset_dungeon();
        } else if (input != ERR) {
            int next_room = choose_next_room();
            if (next_room != dungeon.current_room) {
                move_to_room(next_room);
            }
        } else {
            // auto-move if no input
            int next_room = choose_next_room();
            if (next_room != dungeon.current_room) {
                move_to_room(next_room);
            }
        }
        #else
        input = getchar();
        
        if (input == 'q' || input == 'Q') {
            running = 0;
        } else if (input == 'r' || input == 'R') {
            reset_dungeon();
        } else {
            int next_room = choose_next_room();
            if (next_room != dungeon.current_room) {
                move_to_room(next_room);
            }
        }
        #endif
        
        // check all rooms visited
        if (count_visited_rooms() == dungeon.room_count) {
            #if USE_NCURSES
            mvprintw(GRID_HEIGHT + 4, 0, "Congrat! All rooms explored!");
            refresh();
            #else
            printf("Congrat! All rooms explored!\n");
            #endif
        }
    }
    
    #if USE_NCURSES
    endwin();
    #endif
    
    printf("End\n");
    return 0;
}

