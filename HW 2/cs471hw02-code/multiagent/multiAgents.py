# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
import sys

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        "*** YOUR CODE HERE ***"
        #try sum of reciprocal distances to food
        #try sum of time ghost is scared * distance to ghost
        #penalize if ghost is not scared but in the same position
        if successorGameState.isWin():
            return sys.maxint
        if successorGameState.isLose():
         #   print("Running into ghost!!")
            return -sys.maxint

        score = 0.0
        foodDistance = [manhattanDistance(newPos, food) for food in newFood.asList()]
        width = newFood.width
        height = newFood.height
        factor = (width + height) ** 2
        score += factor/sum(foodDistance)

        for ghostID, ghostState in enumerate(newGhostStates):
            if newScaredTimes[ghostID] > 0:  #encourage pacman to eat scared ghosts
                score += 1000 * newScaredTimes[ghostID] * 1/(1 + util.manhattanDistance(newPos, ghostState.getPosition()))
            else:
                if util.manhattanDistance(newPos, ghostState.getPosition()) == 1:
                    score += -factor
                if util.manhattanDistance(newPos, ghostState.getPosition()) == 2:
                    score += -factor**(1/2)

        return successorGameState.getScore() + score


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        return self.maxValue(gameState, 0)

    def maxValue(self, gameState, depth):
        #print("Max value called on agent 0 at depth %d" %(depth))
        if depth == self.depth:
            return self.evaluationFunction(gameState)
        value = -sys.maxint
        bestAction = None
        legalActions = gameState.getLegalActions(0)
        if len(legalActions) == 0:
            return self.evaluationFunction(gameState)
        for action in legalActions:
            newGameState = gameState.generateSuccessor(0, action)
            result = self.minValue(newGameState, depth, 1)
            if result > value:
                value = result
                bestAction = action
        if depth == 0:
            return bestAction
        return value

    def minValue(self, gameState, depth, agentIndex):
        #print("Min value called on agent %d at depth %d" %(agentIndex, depth))
        value = sys.maxint
        legalActions = gameState.getLegalActions(agentIndex)
        if len(legalActions) == 0:
            return self.evaluationFunction(gameState)
        for action in legalActions:
            newGameState = gameState.generateSuccessor(agentIndex, action)
            if self.lastAgent(agentIndex, gameState):
                value = min(value, self.maxValue(newGameState, depth + 1))
            else:
                value = min(value, self.minValue(newGameState, depth, agentIndex + 1))
        return value

    def lastAgent(self, agentIndex, gameState):
        return (agentIndex + 1) == gameState.getNumAgents()

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        return self.maxValue(gameState, 0, -sys.maxint, sys.maxint)

    def maxValue(self, gameState, depth, alpha, beta):
        #print("Max value called on agent 0 at depth %d" %(depth))
        if depth == self.depth:
            return self.evaluationFunction(gameState)
        value = -sys.maxint
        bestAction = None
        legalActions = gameState.getLegalActions(0)
        if len(legalActions) == 0:
            return self.evaluationFunction(gameState)
        for action in legalActions:
            newGameState = gameState.generateSuccessor(0, action)
            result = self.minValue(newGameState, depth, 1, alpha, beta)
            if result > beta:
                return result
            alpha = max(alpha, result)
            if result > value:
                value = result
                bestAction = action
        if depth == 0:
            return bestAction
        return value

    def minValue(self, gameState, depth, agentIndex, alpha, beta):
        #print("Min value called on agent %d at depth %d" %(agentIndex, depth))
        value = sys.maxint
        legalActions = gameState.getLegalActions(agentIndex)
        if len(legalActions) == 0:
            return self.evaluationFunction(gameState)
        for action in legalActions:
            newGameState = gameState.generateSuccessor(agentIndex, action)
            if self.lastAgent(agentIndex, gameState):
                value = min(value, self.maxValue(newGameState, depth + 1, alpha, beta))
            else:
                value = min(value, self.minValue(newGameState, depth, agentIndex + 1, alpha, beta))
            if value < alpha:
                return value
            beta = min(beta, value)
        return value

    def lastAgent(self, agentIndex, gameState):
        return (agentIndex + 1) == gameState.getNumAgents()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        return self.maxValue(gameState, 0)

    def maxValue(self, gameState, depth):
        if depth == self.depth:
            return self.evaluationFunction(gameState)

        value = -sys.maxint
        bestAction = None
        legalActions = gameState.getLegalActions(0)
        if len(legalActions) == 0:
            return self.evaluationFunction(gameState)
        for action in legalActions:
            newGameState = gameState.generateSuccessor(0, action)
            result = self.chanceValue(newGameState, depth, 1)
            if result > value:
                value = result
                bestAction = action
        if depth == 0:
            return bestAction
        return value

    def chanceValue(self, gameState, depth, agentIndex):
        legalActions = gameState.getLegalActions(agentIndex)
        if len(legalActions) == 0:
            return self.evaluationFunction(gameState)
        prob = 1.0 / len(legalActions)
        expectedValue = 0
        for action in legalActions:
            newGameState = gameState.generateSuccessor(agentIndex, action)
            if self.lastAgent(agentIndex, gameState):
                expectedValue += prob * self.maxValue(newGameState, depth + 1)
            else:
                expectedValue += prob * self.chanceValue(newGameState, depth, agentIndex + 1)
        return expectedValue

    def lastAgent(self, agentIndex, gameState):
        return (agentIndex + 1) == gameState.getNumAgents()

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: Use reciprocal of sum of manhattan distance to all the food pellets. Scale this
      reciprocal by the size of the board.
      If there are any scared ghosts, encourage pacman to move in the direction of these scared ghosts.
      Encouragement is scaled by the scared time left on the ghost. If there is a non-scared ghost,
      discourage pacman from moving too close to it (within 1 or 2 units of Manhattan Distance).
    """
    "*** YOUR CODE HERE ***"
    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    newGhostStates = currentGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    if currentGameState.isWin():
        return sys.maxint
    if currentGameState.isLose():
        #   print("Running into ghost!!")
        return -sys.maxint

    score = 0.0
    foodDistance = [manhattanDistance(newPos, food) for food in newFood.asList()]
    width = newFood.width
    height = newFood.height
    factor = (width + height) ** 2
    score += factor / sum(foodDistance)

    for ghostID, ghostState in enumerate(newGhostStates):
        if newScaredTimes[ghostID] > 0:  # encourage pacman to eat scared ghosts
            score += 1000 * newScaredTimes[ghostID] * 1 / (1 + util.manhattanDistance(newPos, ghostState.getPosition()))
        else:
            if util.manhattanDistance(newPos, ghostState.getPosition()) == 1:
                score += -factor
            if util.manhattanDistance(newPos, ghostState.getPosition()) == 2:
                score += -factor ** (1 / 2)

    return currentGameState.getScore() + score

# Abbreviation
better = betterEvaluationFunction

