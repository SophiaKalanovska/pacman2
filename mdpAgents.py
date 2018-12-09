# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import math
import random
import game
import util
import time

class Grid:

    # Constructor
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

#
# An agent that creates a map.
#
# As currently implemented, the map places a % for each section of
# wall, a * where there is food, and a space character otherwise. That
# makes the display look nice. Other values will probably work better
# for decision making.
#
class MDPAgent(Agent):

    # The constructor. We don't use this to create the map because it
    # doesn't have access to state information.
    def __init__(self):
        self.soFar = 0

    # Method to get the utility of a state
    def getUtility(self,i,j):
        return self.map.getValue(i, j)[1]

    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent.
    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         # states is an array of all grid elements that are not walls
         self.states = []
         # initial food is needed for the utilities
         self.initialFood = 0
         self.addFoodInMap(state)
         self.addWallsToMap(state)
         self.addGhostsToMap(state)
         self.createStates(state)

    # This is what gets run when the game ends.
    def final(self, state):
        print "Finished game"
        print "so far"
        print self.soFar

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)

    # Functions to get the height and the width of the grid.
    def getLayoutHeight(self, corners):
        return max((map(lambda i: corners[i][1], range(len(corners))))) + 1

    def getLayoutWidth(self, corners):
        return max((map(lambda i: corners[i][0], range(len(corners))))) + 1

    # Functions to manipulate the map.
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        map(lambda i: self.map.setValue(walls[i][0], walls[i][1], ('%', '%')), range(len(walls)))

    # Put every element in the list of ghosts elements into the map
    # It has a reward of - the initial food
    def addGhostsToMap(self, state):
        ghost = api.ghosts(state)
        map(lambda i: self.map.setValue(int(ghost[i][0]), int(ghost[i][1]), ( -self.initialFood , 0)), range(len(ghost)))

    # returns if the coordinate (i, j) is a state (not a wall)
    def isLegal(self, i , j):
        if (self.map.getValue(i,j )[1] != ('%')):
            return True
        else:
            return False

    # if the move is legal set the reward and call aroundGhosts with that reward
    def calculateAroundGhost(self, x, y, reward, recursion):
        if self.isLegal(x,y) :
            self.map.setValue(x, y, (reward , 0))
            recursion += 1
            self.aroundGhosts(x, y, reward, recursion)

    # the four blocks around the ghoast have the ancestors reward/2
    def aroundGhosts(self, x, y, reward, recursion,):
        if (x != 0 and x != self.map.getWidth() and y != 0 and y != self.map.getHeight() and recursion < 5):
            newReward = round(reward/2,2)
            listOfDirections = [(x + 1, y),(x - 1, y),(x , y + 1),(x , y - 1)]
            map(lambda (i, j) : self.calculateAroundGhost(i, j, newReward, recursion), listOfDirections)

    # updateGhostsToMap, if the ghost is not scared set the reward - self.initialFood and set
    # four blocks around the ghoast have the ancestors reward/2
    # if it is scared the reward is the same as an empty state
    def updateGhostsToMap(self, state):
        ghost = api.ghosts(state)
        for i in range(len(ghost)):
            if (api.ghostStates(state)[i][1] != 1):
                self.map.setValue(int(ghost[i][0]), int(ghost[i][1]), ( -self.initialFood , 0))
                self.aroundGhosts(int(ghost[i][0]), int(ghost[i][1]),-self.initialFood, 0)
            else:
                self.map.setValue(int(ghost[i][0]), int(ghost[i][1]), ( -0.02 , 0))


    # Create a map with a current picture of the food that exists.
    def addFoodInMap(self, state):
        # First, make all grid elements that aren't walls with a reward - 0.02.
        [self.map.setValue(i, j, ('-0.02', 0))
           for i in range(self.map.getWidth())
           for j in range(self.map.getHeight())]

        food = api.food(state)
        food += api.capsules(state)
        self.initialFood = len(food)
        map(lambda i: self.map.setValue(food[i][0], food[i][1], (self.initialFood, 0)), range(len(food)))


    # the reason of having two methods addFoodInMap and update is
    # update adds -0.02 to the states that are not walls which runs in 0(n), the addFood
    # has a nested for loop, so it runs in O(n^2)
    def updateFoodInMap(self, state):
        # First, make all grid elements thataren't walls with a reward - 0.02.
        map(lambda s: self.map.setValue(s[0], s[1], ('-0.02', 0)) ,self.states)
        food = api.food(state)
        food += api.capsules(state)
        map(lambda i: self.map.setValue(food[i][0], food[i][1], (self.initialFood/len(food), 0)), range(len(food)))

    # After everything is added to the map this method is called (only once in the beggining)
    # to populate the array of all the states that aren't walls
    def createStates(self, state):
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j)[1] != ('%') :
                    self.states.append((i,j))

    #Converts the current direction you are facing to the left of it
    # that is determined by the state you are in and the state you are going to
    def getLeft(self, i, j, x,y):
        if (x+1 == i):
            return (x ,(y + 1))
        elif (x-1 == i):
            return (x ,(y - 1))
        elif (j+1 == y):
            return ((x + 1) ,y)
        else :
            return ((x - 1) ,y)

    #Converts the current direction you are facing to the right of it
    # that is determined by the state you are in and the state you are going to
    def getRight(self, i, j, x,y):
        if (x+1 == i):
            return (x ,(y - 1))
        elif (x-1 == i):
            return (x ,(y + 1))
        elif (j+1 == y):
            return ((x - 1) ,y)
        else :
            return ((x + 1 ),y)


    # if the state you are facing is legal multiply it by the probably
    # if not multipy the current state you are in with the probability
    def expectedUtility(self,i, j,  probability, x,y):
        if self.isLegal(i,j):
            return  probability * self.getUtility(i,j)
        else:
            return  probability * self.getUtility(x, y)


    # the expectedUtility of each direction is the sum of
    def expectedUtilities(self,i, j, x, y):
        utility = 0;

        # 0.8 of the utility of the directon you are facing
        utility += self.expectedUtility(i, j, 0.8, x, y)
        pair = self.getLeft(i, j, x,y)

        # + 0.1 of the utility of the directon to the left of you
        utility += self.expectedUtility(pair[0], pair[1], 0.1, x, y )
        pair = self.getRight(i, j, x,y)

        # + 0.1 of the utility of the directon to the right of you
        utility += self.expectedUtility(pair[0], pair[1], 0.1, x, y )
        return utility


    # the expected utiilityList calculats the utilities of all directions
    # (by calling expectedUtilities)of each of them and returns the list
    def expectedUtilitiesList(self,x, y):
        listOfDirections = [(x + 1, y),(x - 1, y),(x , y + 1),(x , y - 1)]
        return map(lambda (i, j) : round(self.expectedUtilities(i , j, x , y), 2), listOfDirections)




    def Bellman(self, state):
        # get the first float in the grid element (the reward) at the state you are at
        reward = float(self.map.getValue(state[0], state[1])[0])
        # set the value of the second float in the grid element (the utiility) to be equal
        # to the reward + 0.7 of the maxUtility returned from the expected utiilityList
        # the reward of the state doesn't change
        self.map.setValue(state[0], state[1], (reward, float(reward + 0.7 *(max(self.expectedUtilitiesList(state[0], state[1]))))))


    # in the caculation of utilities, the value almost stops changing when you have done
    # the number of current states iterations
    def calculateUtilities(self, state):
        map(lambda k: map( self.Bellman, self.states), range(len(self.states)))


    # I update the food in map, add the ghosts and then calculate the utiities
    # from the legal action I take the bestUtilityand move towards it.
    def getAction(self, state):
        start_time = time.time()
        self.updateFoodInMap(state)
        food = api.food(state)

        # if the food is one only the ghost is added to the map without
        # four blocks around the ghoast to have the ancestors reward/2
        if len(food) == 1 :
            self.map.setValue(food[0][0], food[0][1], (self.initialFood, 0))
            self.addGhostsToMap(state)
        else:
            self.updateGhostsToMap(state)
        self.calculateUtilities(state)


        legal = api.legalActions(state)
        pacman = api.whereAmI(state)
        x = pacman[0]
        y = pacman[1]


        thisdict =	{
          (x + 1, y): Directions.EAST,
          (x - 1, y): Directions.WEST,
          (x , y + 1): Directions.NORTH,
          (x , y - 1): Directions.SOUTH,
          (x,y): Directions.STOP
        }

        # filter the actions that are legal
        legalCoordinates = list(filter(lambda (i, j) : self.isLegal(i,j), thisdict))
        # choooe the best utility
        legalMoveUtility = map(lambda (i, j) : round(self.expectedUtilities(i , j, x , y), 2), legalCoordinates)

        # get the index of it
        indexOfMove = legalMoveUtility.index(max(legalMoveUtility))
        # get the coordinate and do the action that is mapped to in the dictionary
        return api.makeMove(thisdict.get(legalCoordinates[indexOfMove]), legal)
