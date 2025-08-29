from math import log
import random
from time import perf_counter
import sys

POPULATION_SIZE = 500
NUM_CLONES = 1
TOURNAMENT_SIZE = 20
TOURNAMENT_WIN_PROBABILITY = .75
CROSSOVER_LOCATIONS = 5
MUTATION_RATE = .8
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ngram_frequencies = dict()
with open("ngrams.txt") as f:
    for l in f:
        line = l.strip().split()
        ngram_frequencies[line[0]] = line[1]


def encode(message, key):
    uppercase_message = message.upper()
    result = ""
    for char in message:
        if char in ALPHABET:
            ind = ALPHABET.find(char)
            result += key[ind]
        else:
            result += char
    return result


def decode(message, key):
    uppercase_message = message.upper()
    result = ""
    for char in message:
        if char in key:
            ind = key.find(char)
            result += ALPHABET[ind]
        else:
            result += char
    return result

def fitness(message):
    result = 0
    three_grams = []
    for index in range(len(message)-2):
        three_grams.append(message[index:index+3])
    for three_gram in three_grams:
        if three_gram[0] in ALPHABET and three_gram[1] in ALPHABET and three_gram[2] in ALPHABET:
            if three_gram in ngram_frequencies:
                result += log(int(ngram_frequencies[three_gram]),2)
    return result

def swap(s, x1, x2):
    ind1 = s.find(x1)
    ind2 = s.find(x2)
    if ind2 < ind1:
        temp = ind1
        ind1 = ind2
        ind2 = temp
    s = s[:ind1] + s[ind2] + s[ind1+1:ind2] + s[ind1] + s[ind2+1:]
    return s

def breed(p1, p2):
    result = [".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".",".","."]
    temp_list = random.sample(list(p1), CROSSOVER_LOCATIONS)
    for v in temp_list:
        result[p1.find(v)] = v
    ind = result.index(".")
    for letter in p2:
        if letter not in result:
            result[ind] = letter
            if result.count(".")>0:
                ind = result.index(".")
            else:
                break
    return "".join(result)


def mutate(message):
    if random.random() < MUTATION_RATE:
        temp = random.sample(list(message), 2)
        return swap(message, temp[0],temp[1])
    return message
    
def hill_climbing(message):
    generation = 0
    cipherkey = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cipherkey = list(cipherkey)
    random.shuffle(cipherkey)
    cipherkey = "".join(cipherkey)
    result = decode(message, cipherkey)
    fitness_score = fitness(result)
    while generation<500:
        temp_sample = random.sample(list(cipherkey), 2)
        temp_cipherkey = swap(cipherkey, temp_sample[0],temp_sample[1])
        temp_result = decode(message, temp_cipherkey)
        temp_fitness_score = fitness(temp_result)
        if temp_fitness_score>fitness_score:
            fitness_score = temp_fitness_score
            cipherkey = temp_cipherkey
            result = temp_result
            print(result)
        print("Generation:", generation)
        print("Fitness:", fitness_score)
        print("Template:", cipherkey)
        print("Decoded Message:")
        print(result)
        generation += 1
            
def genetic(message):
    generation = 0
    temp_alphabet = list("ETAOINSRHLDCUMFPGWYBVKXJQZ")
    population = ["ETAOINSRHLDCUMFPGWYBVKXJQZ"]
    while len(population)<POPULATION_SIZE:
        random.shuffle(temp_alphabet)
        temp_shuffle = "".join(temp_alphabet)
        if temp_shuffle not in population:
            population.append(temp_shuffle)
    while generation<500:
        fitness_dict = dict()
        for template in population:
            x = fitness(decode(message, template))
            fitness_dict[template] = x
        fitness_dict = dict(sorted(fitness_dict.items(), key=lambda x:x[1], reverse=True))
        next_v = next(iter(fitness_dict.keys()))
        print("Generation:", generation)
        print("Fitness:", fitness_dict[next_v])
        print("Template:", next_v)
        print("Decoded Message:")
        print(decode(message, next_v))
        next_gen = []
        ind = 0
        my_iter = iter(fitness_dict.keys())
        while ind<NUM_CLONES:
            next_gen.append(next(my_iter))
            ind+=1
        while(len(next_gen)<POPULATION_SIZE):
            tourney = random.sample(population, 2*TOURNAMENT_SIZE)
            tourney1 = tourney[:len(tourney)//2]
            ranked_tourney1 = [(fitness_dict[template], template) for template in tourney1]
            ranked_tourney1 = sorted(ranked_tourney1, reverse=True)
            index = 0
            parent1 = ""
            while(True):
                if random.random() < TOURNAMENT_WIN_PROBABILITY:
                    parent1 = ranked_tourney1[index]
                    break
                else:
                    index+=1
            tourney2 = tourney[len(tourney)//2+1:]
            ranked_tourney2 = [(fitness_dict[template], template) for template in tourney2]
            ranked_tourney2 = sorted(ranked_tourney2, reverse=True)
            index = 0
            parent2 = ""
            while(True):
                if random.random() < TOURNAMENT_WIN_PROBABILITY:
                    parent2 = ranked_tourney1[index]
                    break
                else:
                    index+=1
            child = breed(parent1[1],parent2[1])
            child = mutate(child)
            if child not in next_gen:
                next_gen.append(child)
        population = next_gen
        generation+=1

input_algo_selection = input("Do you want hill climbing or genetic? Enter h for hill climbing or g for genetic.\n")
input_message = input("Enter the encoded message:\n")
genetic(input_message) if input_algo_selection.strip() == "g" else hill_climbing(input_message)
