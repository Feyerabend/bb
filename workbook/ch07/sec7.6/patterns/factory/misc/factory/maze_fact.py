from abc import ABC, abstractmethod
from typing import List

class Room:
    def __init__(self, number: int):
        self.number = number
        self.sides = {}  # direction -> MapSite

    def set_side(self, direction: str, site):
        self.sides[direction] = site

class Wall:
    pass

class Door:
    def __init__(self, r1: Room, r2: Room):
        self.room1 = r1
        self.room2 = r2

class Maze:
    def __init__(self):
        self.rooms: List[Room] = []

    def add_room(self, room: Room):
        self.rooms.append(room)


# Abstract Factory – creates family of related products

class MazeFactory(ABC):
    @abstractmethod
    def make_maze(self) -> Maze:
        pass

    @abstractmethod
    def make_room(self, number: int) -> Room:
        pass

    @abstractmethod
    def make_wall(self) -> Wall:
        pass

    @abstractmethod
    def make_door(self, r1: Room, r2: Room) -> Door:
        pass


class StandardMazeFactory(MazeFactory):
    def make_maze(self) -> Maze:
        return Maze()

    def make_room(self, number: int) -> Room:
        return Room(number)

    def make_wall(self) -> Wall:
        return Wall()

    def make_door(self, r1: Room, r2: Room) -> Door:
        return Door(r1, r2)


class EnchantedMazeFactory(MazeFactory):
    def make_maze(self) -> Maze:
        return Maze()  # could be EnchantedMaze

    def make_room(self, number: int) -> Room:
        return Room(number)  # could return EnchantedRoom

    def make_wall(self) -> Wall:
        return Wall()  # could be SpelledWall

    def make_door(self, r1: Room, r2: Room) -> Door:
        return Door(r1, r2)  # could be EnchantedDoor that needs spell


# The "algorithm" of building a maze – independent of concrete parts
def create_simple_maze(factory: MazeFactory) -> Maze:
    maze = factory.make_maze()

    r1 = factory.make_room(1)
    r2 = factory.make_room(2)

    door = factory.make_door(r1, r2)

    maze.add_room(r1)
    maze.add_room(r2)

    r1.set_side("north", factory.make_wall())
    r1.set_side("east",  door)
    r1.set_side("south", factory.make_wall())
    r1.set_side("west",  factory.make_wall())

    r2.set_side("north", factory.make_wall())
    r2.set_side("west",  door)
    r2.set_side("south", factory.make_wall())
    r2.set_side("east",  factory.make_wall())

    return maze


# Usage
standard_maze = create_simple_maze(StandardMazeFactory())
enchanted_maze = create_simple_maze(EnchantedMazeFactory())
