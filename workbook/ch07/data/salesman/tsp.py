import random
import math

# random coordinates for cities
def generate_cities(num_cities, seed=42):
    random.seed(seed)
    return [(random.randint(0, 100), random.randint(0, 100)) for _ in range(num_cities)]

# Euclidean distance between two cities
def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

# total length of a route
def route_length(route, cities):
    return sum(distance(cities[route[i]], cities[route[i+1]]) for i in range(len(route) - 1)) + distance(cities[route[-1]], cities[route[0]])

# initial random population
def create_population(size, num_cities):
    return [random.sample(range(num_cities), num_cities) for _ in range(size)]

# select parents using tournament selection
def select_parents(population, cities):
    tournament_size = 5
    selected = random.sample(population, tournament_size)
    return min(selected, key=lambda route: route_length(route, cities))

# perform ordered crossover (OX)
def crossover(parent1, parent2):
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [-1] * size
    child[start:end] = parent1[start:end]
    p2_index = 0
    for i in range(size):
        if child[i] == -1:
            while parent2[p2_index] in child:
                p2_index += 1
            child[i] = parent2[p2_index]
    return child

# mutate by swapping two cities
def mutate(route, mutation_rate=0.1):
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
    return route

# genetic algorithm for TSP
def genetic_algorithm(num_cities, population_size=100, generations=500):
    cities = generate_cities(num_cities)
    population = create_population(population_size, num_cities)
    
    for _ in range(generations):
        new_population = []
        for _ in range(population_size // 2):
            parent1 = select_parents(population, cities)
            parent2 = select_parents(population, cities)
            child1 = mutate(crossover(parent1, parent2))
            child2 = mutate(crossover(parent2, parent1))
            new_population.extend([child1, child2])
        population = new_population
    
    best_route = min(population, key=lambda route: route_length(route, cities))
    return best_route, route_length(best_route, cities), cities


best_route, best_distance, cities = genetic_algorithm(num_cities=10)
print("Best route:", best_route)
print("Best distance:", best_distance)
