import random
import os
import time


MAP = [	[1,1,1,1,1,1,1,1],
		[1,9,9,9,9,9,9,1],
		[1,9,0,0,0,0,9,1],
		[1,9,0,0,0,9,1,1],
		[1,9,0,0,0,9,1,1],
		[1,9,0,0,0,0,9,1],
		[1,9,9,9,9,9,9,1],
		[1,1,1,1,1,1,1,1]]


def fill_hpos():
	arr = []
	for y in range(8):
		for x in range(8):
			if MAP[y][x] == 9:
				arr.append([y,x])
	return arr

H_POS = fill_hpos()
NORTH = [-1, 0]
SOUTH = [1, 0]
EAST = [0, 1]
WEST = [0, -1]

CHAR_NORTH = '^'
CHAR_SOUTH = 'v'
CHAR_EAST = '>'
CHAR_WEST = '<'


NOP = 0b00
FORWARD = 0b01
ROT_RIGHT = 0b10
ROT_LEFT = 0b11

MAX_CYCLES = 28
MAX_GENERATIONS = 50
MAX_POP = 20
MUT_RATE = 50


class Agent:
	x = 1
	y = 1
	vec = EAST
	char = CHAR_EAST
	
	def sense(self):
		sensors = 0
		if self.vec == EAST:
			#left
			if MAP[self.y-1][self.x] == 1:
				sensors = sensors | 0x01
			#left-diag
			if MAP[self.y-1][self.x+1] == 1:
				sensors = sensors | 0x02
			#front
			if MAP[self.y][self.x+1] == 1:
				sensors = sensors | 0x04
			#right-diag
			if MAP[self.y+1][self.x+1] == 1:
				sensors = sensors | 0x08
			#right
			if MAP[self.y+1][self.x] == 1:
				sensors = sensors | 0x10

		elif self.vec == WEST:
			#left
			if MAP[self.y+1][self.x] == 1:
				sensors = sensors | 0x01
			#left-diag
			if MAP[self.y+1][self.x-1] == 1:
				sensors = sensors | 0x02
			#front
			if MAP[self.y][self.x-1] == 1:
				sensors = sensors | 0x04
			#right-diag
			if MAP[self.y-1][self.x-1] == 1:
				sensors = sensors | 0x08
			#right
			if MAP[self.y-1][self.x] == 1:
				sensors = sensors | 0x10

		elif self.vec == NORTH:
			#left
			if MAP[self.y][self.x-1] == 1:
				sensors = sensors | 0x01
			#left-diag
			if MAP[self.y-1][self.x-1] == 1:
				sensors = sensors | 0x02
			#front
			if MAP[self.y-1][self.x] == 1:
				sensors = sensors | 0x04
			#right-diag
			if MAP[self.y-1][self.x+1] == 1:
				sensors = sensors | 0x08
			#right
			if MAP[self.y][self.x+1] == 1:
				sensors = sensors | 0x10

		elif self.vec == SOUTH:
			#left
			if MAP[self.y][self.x+1] == 1:
				sensors = sensors | 0x01
			#left-diag
			if MAP[self.y+1][self.x+1] == 1:
				sensors = sensors | 0x02
			#front
			if MAP[self.y+1][self.x] == 1:
				sensors = sensors | 0x04
			#right-diag
			if MAP[self.y+1][self.x-1] == 1:
				sensors = sensors | 0x08
			#right
			if MAP[self.y][self.x-1] == 1:
				sensors = sensors | 0x10

		return sensors
		


	def act(self, action):
		if action == FORWARD:
			new_x = self.x + self.vec[1]
			new_y = self.y + self.vec[0]

			if MAP[new_y][new_x] == 1:
				return

			self.x = new_x
			self.y = new_y

		elif action == ROT_RIGHT:
			if self.vec == NORTH:
				self.vec = EAST
				self.char = CHAR_EAST
			elif self.vec == SOUTH:
				self.vec = WEST
				self.char = CHAR_WEST
			elif self.vec == EAST:
				self.vec = SOUTH
				self.char = CHAR_SOUTH			
			elif self.vec == WEST:
				self.vec = NORTH
				self.char = CHAR_NORTH

		elif action == ROT_LEFT:
			if self.vec == NORTH:
				self.vec = WEST
				self.char = CHAR_WEST
			elif self.vec == SOUTH:
				self.vec = EAST
				self.char = CHAR_EAST
			elif self.vec == EAST:
				self.vec = NORTH
				self.char = CHAR_NORTH			
			elif self.vec == WEST:
				self.vec = SOUTH
				self.char = CHAR_SOUTH

		elif action == NOP:
			return



def init_population(sz):
	arr = []
	for i in range(sz):
		arr.append(random.randint(0x8000000000000000, 0xffffffffffffffff))

	return arr


def calc_fitness(gene, cycles):
	agent = Agent()
	score = 0
	visited = []
	for i in range(cycles):
		last_pos = [agent.y, agent.x]
		visited.append(last_pos)
		wall_config = agent.sense()
		action = (gene >> (wall_config * 2)) & 0x03
		agent.act(action)
		curr_pos = [agent.y, agent.x]
		if curr_pos != last_pos and curr_pos not in visited and curr_pos in H_POS:
				score += 1

	return score



def sort_by_fitness(individuals, gen):
	fitness_list = []
	sorted_fittest = []
	for i in range(len(individuals)):
		fitness_list.append((individuals[i], calc_fitness(individuals[i], MAX_CYCLES), gen))

	sorted_fittest = sorted(fitness_list, key = lambda ind: ind[1], reverse = True)
	return sorted_fittest

MASK = 0xffffffffffffffff


def mutate(gene):
	prob_mut = MUT_RATE
	mut = 0
	new_gene = gene
	for i in range (64):
		 if random.randint(1, 1000) > prob_mut:
		 	mut = 0
		 else:
		 	mut = 1

		 new_gene = new_gene ^ (mut << i & 0xffffffffffffffff)
	return new_gene



def crossover_mutate(gene1, gene2, p):

	head_mask = (MASK << p) & MASK
	tail_mask = MASK - head_mask
	g1_head = gene1 & head_mask
	g2_head = gene2 & head_mask
	g1_tail = gene1 & tail_mask
	g2_tail = gene2 & tail_mask


	return [mutate(g1_head | g2_tail), mutate(g2_head | g1_tail)]


def breed(individuals):
	children = []
	length = len(individuals)
	for i in range(length):
		cross_point = random.randint(1, 63)
		p1 = individuals[i]
		p2 = individuals[(i+1) % length]
		children += crossover_mutate(p1, p2, cross_point)

	return children


def print_gen(pop, gen):
	print "---------GEN "+ str(gen) +"------------------------"
	for i in range(len(pop)):
		print bin(pop[i][0]),
		print "\t" + str(pop[i][1])



def render(m, agent):
	for y in range(8):
		for x in range(8):
			if [x, y] == [agent.x, agent.y]:
				print agent.char,
			else:
				print m[y][x],
		print ""



def create_printable_map(m):
	char_map = []
	row = ""
	for y in range(8):
		for x in range(8):
			if m[y][x] == 1:
				row += 'O'
			else:
				row += ' '
		char_map.append(row)
		row = ""

	return char_map

def sim(gene, cycles):
	m = create_printable_map(MAP)
	agent = Agent()
	for i in range(cycles):
		os.system('clear')
		render(m, agent)
		wall_config = agent.sense()
		action = (gene >> (wall_config * 2)) & 0x03
		agent.act(action)

		time.sleep(0.5)


#-----------------------------------------------------------------------

def main():

	pop_size = MAX_POP
	curr_gen = []
	new_gen = []
	mating_pool = []
	fittest = (0x0000000000000000, 0, 0)
	n_gen = 0

	curr_gen = init_population(pop_size)

	while fittest[1] != 19:

		fittest_first = sort_by_fitness(curr_gen, n_gen)

		print_gen(fittest_first, n_gen)

		if fittest_first[0][1] > fittest[1]:
		 	fittest = fittest_first[0]


		mating_pool = fittest_first[:pop_size/2]

		new_gen = breed([i[0] for i in mating_pool])

		curr_gen = new_gen

		n_gen += 1

	return fittest

optimal = main()


print ""
print "OPTIMAL SOLUTION FOUND IN GENERATION " + str(optimal[2]) 
print "(solution, fitness, generation) = " + str(optimal)


for i in range(10):
	print "SIMULATING OPTIMAL SOLUTION IN " + str(10-i) + " SECONDS"
	time.sleep(1)

test_gene = optimal[0]
sim(test_gene, MAX_CYCLES+2)
