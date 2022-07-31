
from mineField import MineField,ExplosionException
from mineField import BEGINNER_FIELD,INTERMEDIATE_FIELD,EXPERT_FIELD
from enum import IntEnum
from collections import namedtuple
import logging

class Cell(IntEnum):
	Bomb = -99
	Unknown = -1
	Safe=0
	OneBombAdjacent=1
	TwoBombAdjacent=2
	ThreeBombAdjacent=3
	#etc..
	
Point = namedtuple('Point', ['x', 'y'])

class Solver:
	def __init__(self, setting):
		'''Create class with Field settings'''
		self.setting=setting
		self.mine_count = setting['number_of_mines']
		self.w=setting['width']
		self.h=setting['height']
		self.games=0				#current game

					
	def newGame(self):
		'''Create a MineField object and try to solve it'''
		self.field = MineField(**self.setting)
		self.mines_left = self.mine_count
		self.chart = [ [Cell.Unknown] * self.w for _ in range(self.h) ]
		
		#Local representation
		self.games +=1
		self.mines = []
		
		logging.debug(f"------Game #{self.games}-----")
		
		#Solving logic
		walklist = [Point(0,0)] # we start walking in the topleft corner
		try:
			while self.mines_left>0:
				while len(walklist)>0:
				
					#State 1: sweep all squares without adjacent mines
					pt = walklist.pop()	
					self.walk(pt) 
					
					#State 2: find all squares with adjacent mines
					for x in range(self.w):
						for y in range(self.h):
							if self.chart[y][x] >= Cell.OneBombAdjacent: #this cell has one or more adjacent mines
								walklist.extend(self.count(Point(x,y)))
				#We have walked all squares without guesswork.
				#Larger grids might not be solvable without guessing. add more points to the walklist until mines_left = 0 (or you explode ;) )
				
				if self.mines_left>0:
					self.pprint()
					for x in range(self.w-1,0,-1):
							for y in range(self.h-1,0,-1):
								if self.chart[y][x] >= Cell.Unknown: #Not opened before
									walklist.append(Point(x,y))
									logging.warning(f"Took a guess! {Point(x,y)}!")
									continue
								
			self.pprint()
		except:
			pass
		finally:
			return self.mines

	def walk(self,pos):
		'''Sweep a cell, and walk all empty neighbours'''

		#Position is outside the board, or already visited
		if not self.isValidPos(pos) or self.chart[pos.y][pos.x]!=Cell.Unknown:
			return
						
		try:
			num = self.field.sweep_cell(pos.x,pos.y)
			if num>0:
  				self.chart[pos.y][pos.x]=num #number of adjacent mines
			else:
				#No mines adjacent
				self.chart[pos.y][pos.x]=Cell.Safe
				self.walk(Point(pos.x+1,pos.y-1))
				self.walk(Point(pos.x+1,pos.y))
				self.walk(Point(pos.x+1,pos.y+1))
				
				self.walk(Point(pos.x-1,pos.y-1))
				self.walk(Point(pos.x-1,pos.y))
				self.walk(Point(pos.x-1,pos.y+1))
				
				self.walk(Point(pos.x,pos.y-1))
				self.walk(Point(pos.x,pos.y+1))
		except ExplosionException:
			logging.error(f"Bomb at ({pos}) exploded!")
			self.chart[pos.y][pos.x]=Cell.Bomb
			self.mines.append(pos)
			raise Exception('Game ended')

			
	def count(self,pos):
		'''Count neighbours and deduce locations'''

		neighbours=[] #all neigbour cells
		neighbours.append(Point(pos.x-1,pos.y-1))
		neighbours.append(Point(pos.x,pos.y-1))
		neighbours.append(Point(pos.x+1,pos.y-1))
		neighbours.append(Point(pos.x-1,pos.y))
		neighbours.append(Point(pos.x+1,pos.y))
		neighbours.append(Point(pos.x-1,pos.y+1))
		neighbours.append(Point(pos.x,pos.y+1))
		neighbours.append(Point(pos.x+1,pos.y+1))
		
		result = []
		
		#filter neighbours that have not been swept or are already marked as bomb
		unknowns = [pt for pt in neighbours if self.isValidPos(pt) and self.chart[pt.y][pt.x]<=Cell.Unknown]

		#we have a list of neighbours. If the number of bombs is equal to the amount of neighbours, all are bombs.
		if self.chart[pos.y][pos.x] == len(unknowns):
			for cell in unknowns:
				if self.chart[cell[1]][cell[0]]!=Cell.Bomb: #we have not marked this mine
					logging.info(f"Bomb at ({cell})")
					self.chart[cell.y][cell.x]=Cell.Bomb
					self.mines.append(pos)
					self.mines_left-=1
				
		#filter neighbours that are marked bombs
		bombs = [pt for pt in neighbours if self.isValidPos(pt) and self.chart[pt.y][pt.x]==Cell.Bomb]

		#if the sum of adjacent bombs is equal to the number of marked bombs, other neighbours can't be bombs
		if self.chart[pos.y][pos.x] == len(bombs):
			for cell in unknowns:
				if self.chart[cell[1]][cell[0]]!=Cell.Bomb: #we have not marked this as mine
					result.append(cell)
			 	
		#list of cells that are not bombs, and need to be walked
		return result
		
	def isValidPos(self,pos):
		'''Position is inside minefield'''
		return (pos.x>=0) and (pos.x<self.w) and (pos.y>=0) and (pos.y<self.h)
			
	def pprint(self):
		'''Pretty print local field'''
		res="Minefield\n"
		for row in self.chart:
			for char in row:
				if char == Cell.Bomb:
					res+="*"
				elif char == Cell.Unknown:
					res+="."
				elif char == Cell.Safe:
					res+=" "
				else:
					res+=str(char)
			res+="\n"
		logging.debug(res)	
		logging.debug(f"{self.mines_left} bombs remaining")


if __name__ == "__main__":

	#INFO  | Show mine locations
	#DEBUG | Show map of playing board
	#ERROR | Only explosion
	logging.basicConfig(level=logging.DEBUG)

	#Create a solver object, play x games
	s = Solver(BEGINNER_FIELD)
	for i in range(10):
		print(s.newGame())
	
	#Create object, play one game
	#Solver(INTERMEDIATE_FIELD)
	
	#etc.	
	Solver(EXPERT_FIELD).newGame()
	
	#custom grid
	#Solver({'width':30,'height':30,'number_of_mines':10})
