
# A simplified version of Maze Builder example

class Maze:
    def __init__(self):
        self.rooms = {}
        self.doors = []

    def add_room(self, room):
        self.rooms[room.number] = room

    def add_door(self, room1, room2, direction):
        self.doors.append((room1, room2, direction))

    def __str__(self):
        return f"Maze with {len(self.rooms)} rooms and {len(self.doors)} doors"


class MazeBuilder:
    def __init__(self):
        self.maze = Maze()

    def build_room(self, number):
        # In real version: create Room object, set sides, etc.
        self.maze.add_room(type('Room', (), {'number': number}))
        return self

    def build_door(self, r1, r2, direction="east"):
        self.maze.add_door(r1, r2, direction)
        return self

    def build(self):
        return self.maze


class MazeDirector:
    def construct_simple_maze(self, builder: MazeBuilder):
        (builder.build_room(1)
               .build_room(2)
               .build_door(1, 2, "east")
               .build_room(3)
               .build_door(2, 3, "south"))
        return builder.build()

    def construct_bigger_maze(self, builder):
        # longer sequence → different "algorithm" variant
        (builder.build_room(1)
               .build_room(2)
               .build_door(1, 2)
               .build_room(3)
               .build_door(2, 3)
               .build_room(4)
               .build_door(3, 4, "west")
               .build_room(5)
               .build_door(4, 5))
        return builder.build()


# Usage — feels like running different "maze generation algorithms"
builder = MazeBuilder()
director = MazeDirector()

small = director.construct_simple_maze(builder)
print(small)   # Maze with 3 rooms and 2 doors

# reset builder or use new one
builder = MazeBuilder()
big = director.construct_bigger_maze(builder)
print(big)     # Maze with 5 rooms and 4 doors
