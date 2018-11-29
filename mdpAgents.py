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
import random
import game
import util
class Grid:

    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
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

    # Print the grid out.
    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j][1],
            # A new line after each line of the grid
            print
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j][1],
            # A new line after each line of the grid
            print
        # A line after the grid
        print

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
        self.last= Directions.STOP
        print "Running init!"


    def getUtility(self,i,j):
        return self.map.getValue(i, j)[1]

    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent.
    def registerInitialState(self, state):
         print "Running registerInitialState!"
         # Make a map of the right size
         self.makeMap(state)
         self.states = []
         self.addFoodInMap(state)
         self.addWallsToMap(state)
         self.addGhostsToMap(state)
         self.map.display()
         print "----------------------------------------------"

    # This is what gets run when the game ends.
    def final(self, state):
        print "Looks like I just died!"

    # Make a map by creating a grid of the right size
    def makeMap(self,state):
        corners = api.corners(state)
        print corners
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height)

    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], ('%', '%'))

    def addGhostsToMap(self, state):
        ghost = api.ghosts(state)
        for i in range(len(ghost)):
            self.map.setValue(int(ghost[i][0]), int(ghost[i][1]), ('-5', 0))



    # Create a map with a current picture of the food that exists.
    def addFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.

        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                # print self.map.getValue(i, j)
                # if self.map.getValue(i, j)[0] != ('%') :
                self.map.setValue(i, j, ('0.03', 0))

        # ghost = api.ghosts(state)
        # for i in range(len(ghost)):
        #     self.map.setValue(int (ghost[i][0]), int (ghost[i][1]), ('-1', -1))

        food = api.food(state)
        for i in range(len(food)):

            self.map.setValue(food[i][0], food[i][1], ('1', 0))



    def getLeft(self,i,j):
        if (self.last == Directions.NORTH):
            self.last = Directions.WEST
            # return((i - 1), j )
        elif (self.last == Directions.SOUTH):
            self.last = Directions.EAST
            # return((i + 1), j)
        elif (self.last == Directions.EAST):
            self.last = Directions.NORTH
            # return(i , (j + 1))
        else :
            self.last = Directions.SOUTH
            # return(i,(j - 1))

    def getRight(self,i,j):
        if (self.last == Directions.NORTH):
            self.last = Directions.EAST
            # return((i + 1), j)

        elif (self.last == Directions.SOUTH):
            self.last = Directions.WEST
            # return((i - 1), j )

        elif (self.last == Directions.EAST):
            self.last = Directions.SOUTH
            # return(i,(j - 1))
        else :
            self.last = Directions.NORTH
            return(i , (j + 1))

    def expectedUtility(self,i, j, probablility):

        if self.map.getValue(i, j)[1] != ('%'):
            if (self.last == Directions.NORTH) and self.map.getValue(i,(j + 1))[1] != ('%'):
                return  probablility * self.getUtility(i,(j + 1))
            elif (self.last == Directions.SOUTH) and self.map.getValue(i,(j - 1))[1] != ('%'):
                return  probablility * self.getUtility(i,(j - 1))
            elif (self.last == Directions.EAST)and self.map.getValue((i +1),j)[1] != ('%'):
                return  probablility * self.getUtility((i +1),j)
            elif (self.last == Directions.WEST)and self.map.getValue((i -1),j)[1] != ('%'):
                return  probablility * self.getUtility((i -1),j)
            else:
                return probablility * self.getUtility(i,j)
        else:
            return "*"

    def expectedUtilities(self,i, j):
        utility = 0;
        utility += self.expectedUtility(i, j, 0.8)
        self.getLeft(i, j)
        utility += self.expectedUtility(i, j, 0.1)
        self.getRight(i, j)
        utility += self.expectedUtility(i, j, 0.1)
        # left = self.getLeft(i, j)
        # if ( self.expectedUtility(left[0], left[1], 0.1) != "*" ):
        #     utility += self.expectedUtility(left[0], left[1], 0.1)
        # else:
        #     utility += self.expectedUtility(i, j, 0.1)
        #
        # right = self.getRight(i, j)
        #
        # if ( self.expectedUtility(right[0], right[1], 0.1) != "*" ):
        #     utility += self.expectedUtility(right[0], right[1], 0.1)
        # else:
        #     utility += self.expectedUtility(i, j, 0.1)


        return utility



    def expectedUtilitiesList(self,i, j):
        expectedUtilitiesList =[]


        self.last= Directions.NORTH
        expectedUtilitiesList.append(self.expectedUtilities(i , j))
        self.last= Directions.SOUTH
        expectedUtilitiesList.append(self.expectedUtilities(i , j))
        self.last= Directions.EAST
        expectedUtilitiesList.append( self.expectedUtilities(i , j))
        self.last= Directions.WEST
        expectedUtilitiesList.append( self.expectedUtilities(i , j))
        return expectedUtilitiesList


    def Bellman(self, state):
        reward = float(self.map.getValue(state[0], state[1])[0])
        maxUtility = self.expectedUtilitiesList(state[0], state[1])
        self.map.setValue(state[0], state[1], (reward, float(reward + 0.7 * max(maxUtility))))



    def calculateUtilities(self, state):
        for k in range(len(self.states)):

            for state in self.states:
                self.Bellman(state)


    def updateFoodInMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j)[1] != ('%') :
                    self.states.append((i,j))
                    self.map.setValue(i, j, ('-0.03', 0))

        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], ('1', 0))

    def north(self, legal):
        if (Directions.NORTH in legal):
            return api.makeMove(Directions.NORTH, legal)
        else :
            return api.makeMove(Directions.STOP, legal)

    def south(self, legal):
        if (Directions.SOUTH in legal):
            return api.makeMove(Directions.SOUTH, legal)
        else :
            return api.makeMove(Directions.STOP, legal)

    def east(self, legal):
        if (Directions.EAST in legal):
            return api.makeMove(Directions.EAST, legal)
        else :
            return api.makeMove(Directions.STOP, legal)

    def west(self, legal):
        if (Directions.WEST in legal):
            return api.makeMove(Directions.WEST, legal)
        else :
            return api.makeMove(Directions.STOP, legal)

    def stop():
        return api.makeMove(Directions.STOP, legal)


    def move(self,argument, legal):
        if (argument == 0):
            return self.north(legal)
        elif (argument == 1):
            return self.south(legal)
        elif (argument == 2):
            return self.east(legal)
        elif (argument == 3):
            return self.west(legal)
        else:
            return self.stop

    # For now I just move randomly, but I display the map to show my progress
    def getAction(self, state):
        self.updateFoodInMap(state)
        self.addGhostsToMap(state)

        self.calculateUtilities(state)
        # print "---------------------------------------"
        # self.map.prettyDisplay()
        # print "---------------------------------------"
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)


        pacman = api.whereAmI(state)

        maxUtility = self.expectedUtilitiesList(pacman[0], pacman[1])
        pacmanUtility = self.map.getValue(pacman[0], pacman[1])[1]
        maxUtility.append(pacmanUtility)

        return self.move(maxUtility.index(max(maxUtility)), legal)
        #     legal.remove(Directions.STOP)
        # # Random choice between the legal options.
        # return api.makeMove(random.choice(legal), legal)
