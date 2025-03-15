#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define INF 1000000
#define MAX_NODES 100

typedef struct {
    int x, y;
} Point;

typedef struct {
    int f, g, h;
    int parent_x, parent_y;
    int open;
} Node;

Node grid[MAX_NODES][MAX_NODES];

int isValid(int x, int y, int rows, int cols) {
    return (x >= 0 && x < rows && y >= 0 && y < cols);
}

int heuristic(Point a, Point b) {
    return abs(a.x - b.x) + abs(a.y - b.y);
}

void aStar(int gridMap[MAX_NODES][MAX_NODES], int rows, int cols, Point start, Point goal) {
    int dx[] = {-1, 1, 0, 0};
    int dy[] = {0, 0, -1, 1};

    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++) {
            grid[i][j].f = INF;
            grid[i][j].g = INF;
            grid[i][j].h = 0;
            grid[i][j].open = 0;
            grid[i][j].parent_x = -1;
            grid[i][j].parent_y = -1;
        }

    grid[start.x][start.y].g = 0;
    grid[start.x][start.y].h = heuristic(start, goal);
    grid[start.x][start.y].f = grid[start.x][start.y].h;
    grid[start.x][start.y].open = 1;

    while (1) {
        int minF = INF, currentX = -1, currentY = -1;

        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++)
                if (grid[i][j].open && grid[i][j].f < minF) {
                    minF = grid[i][j].f;
                    currentX = i;
                    currentY = j;
                }

        if (currentX == -1)
            break;

        grid[currentX][currentY].open = 0;

        if (currentX == goal.x && currentY == goal.y) {
            printf("Path found!\n");
            return;
        }

        for (int i = 0; i < 4; i++) {
            int nx = currentX + dx[i], ny = currentY + dy[i];

            if (isValid(nx, ny, rows, cols) && gridMap[nx][ny] == 0) {
                int gNew = grid[currentX][currentY].g + 1;
                int hNew = heuristic((Point){nx, ny}, goal);
                int fNew = gNew + hNew;

                if (grid[nx][ny].f == INF || fNew < grid[nx][ny].f) {
                    grid[nx][ny].g = gNew;
                    grid[nx][ny].h = hNew;
                    grid[nx][ny].f = fNew;
                    grid[nx][ny].parent_x = currentX;
                    grid[nx][ny].parent_y = currentY;
                    grid[nx][ny].open = 1;
                }
            }
        }
    }

    printf("No path found!\n");
}

int main() {
    int gridMap[MAX_NODES][MAX_NODES] = {{0}};
    Point start = {0, 0}, goal = {4, 4};
    aStar(gridMap, 5, 5, start, goal);
    return 0;
}