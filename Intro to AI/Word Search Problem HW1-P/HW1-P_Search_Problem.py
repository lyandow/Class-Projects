import sys
"""
Author: Louden Yandow

HW1-P_Search_Problem.py takes in a word from the user, as well
as a goal word from the user. It then conducts an A* search to 
determine the best possible path from the start word to the goal
word where you can only change one letter at a time, in addition
that each word after a letter change MUST be a legitimate English
word. This would be based on the dictionary file provided as
a command line argument by the user.
"""

# determines the total cost (the distance) the current
# word is from the goal

# :param str1     the word of the current state
# :param str2     the goal word

class WordState:
    """
    WordState is a class used to model a node for the A* search algorithm.
    It contains the word, a parent node, any child nodes, and the various
    costs used in A* search.
    """
    def __init__(self, word, parentNode, heuristicCost):
        self.word = word
        self.parentNode = parentNode
        self.childNodes = {}

        # h(n)
        self.heuristicCost = heuristicCost

        # g(n)
        if parentNode is None:
            self.gCost = 0
        else:
            self.gCost = parentNode.gCost + 1

        # f(n) = h(n) + g(n)
        self.totalCost = self.heuristicCost + self.gCost


def cost(currentWord, goalWord):
    """
    Measure the heuristic cost between the node and the goal node
    based on the number of different letters at different indexes in the strings
    :param currentWord: The node we are measuring cost for
    :param goalWord:    The goal node
    :return:    heuristic cost from this node to the goal
    """

    # Find the heuristic cost from currentWord to goalWord based on different letters
    totalCost = 0
    if len(currentWord) == len(goalWord):
        for i in range(len(currentWord)):
            if currentWord[i] != goalWord[i]:
                totalCost += 1
    else:
        return -1
    return totalCost


def assembleTree(parentState, noRepeatNodes, dictionary, goalState):
    """
    Assemble a one level tree extending from the root node. I originally wanted to
    implement this recursively, but couldn't find a way to fix a major design problem
    where only the first child of each parent is going to produce children, resulting in
    a horrible, single path tree.
    :param parentState:     The Parent node to construct children from
    :param noRepeatNodes:   A list of previously constructed children, used to prevent duplicates
    :param dictionary:      The dictionary used from user input
    :param goalState:       The state we are going to search for, used to measure heuristic costs
    :return:    nothing
    """

    # noRepeatNodes ensures we do not create duplicate children
    noRepeatNodes[parentState.word] = 1
    tempWord = list(parentState.word)
    wordLen = len(parentState.word)
    childrenWords = {}

    # Generate all possible words that are exactly one letter different from the word we started with
    for i in range(wordLen):
        tempWord = list(parentState.word)
        for x in range(26):
            tempWord[i] = chr(97 + x)
            tempWordString = str("".join(tempWord))

            # Check if the new word is a legitimate English word (based on our dictionary)
            if tempWordString in dictionary:
                childrenWords[tempWordString] = tempWordString

    # Construct the tree structure for the children and parent nodes
    for child in childrenWords:
        if child not in noRepeatNodes:
            newChildWordState = WordState(child, parentState, cost(child, goalState.word))
            parentState.childNodes[newChildWordState] = newChildWordState

            # noRepeatNodes ensures a child does not create a child that is a clone of its direct sibling
            noRepeatNodes[child] = 1

    return


def aStar(start, goal, noRepeatNodes, dictionary):
    """
    Conduct A* search from the starting state/node to the goal state/node.
    :param start:   Starting node (WordState)
    :param goal:    Goal node (WordState)
    :param noRepeatNodes:   list of nodes used so we do not create duplicate children
    :param dictionary:      dictionary file gathered from user input
    :return:    the path from starting node to the goal node.
    """

    # Visited and unvisited sets so we don't get stuck in loops
    notVisited = set()
    visited = set()

    # Current WordState is the starting WordState
    current = start

    # Current WordState is not visited yet.
    notVisited.add(current)

    # While we still have nodes to visit
    while notVisited:
        # Select the current, lowest cost node closest to the goal state
        current = min(notVisited, key=lambda wordState:wordState.totalCost)
        # Return the path to the goal state if we have found the goal state
        if current.word == goal.word:
            pathToGoal = []
            while current.parentNode:
                pathToGoal.append(current)
                current = current.parentNode
            pathToGoal.append(current)
            return pathToGoal[::-1]

        # Now this state has been visited, move it to visited set.
        notVisited.remove(current)
        visited.add(current)

        # Construct the tree from the current WordState to get proper child nodes.
        assembleTree(current, noRepeatNodes, dictionary, goalState)

        # Determine which children to visit.
        for child in current.childNodes:
            if child in visited:
                continue
            else:
                notVisited.add(child)
    raise ValueError("No path found from " + start.word + " to " + goal.word)

if __name__ == '__main__':
    """
    This is the main method. It is setting up the states
    needed to conduct the A* search from the user-input starting word
    to the goal word. Afterword, it prints relevant information to the search.
    
    It is important to note that this program expects a dictionary file as a command
    line argument!
    """

    # Gather input words from user
    startWord = input("Please enter the starting word: ")
    goalWord = input("Please enter the goal word: ")

    # construct start and goal states
    initialState = WordState(startWord, None, cost(startWord, goalWord))
    goalState = WordState(goalWord, None, 0)

    # Usage checks....
    if initialState.word == goalState.word:
        print("Both words are the same. No search needed.")
        exit(0)
    initialCost = cost(initialState.word, goalState.word)
    if initialCost < 0:
        print("ERROR: Mismatching word sizes. Terminating")
        exit(1)

    # Show originaly heuristic difference
    print("Initial character-wise difference is: " + str(initialCost))

    # Open the dictionary file, convert it to usable form of strings
    dictFile = open(sys.argv[1], "r")
    dictionary = {}
    for line in dictFile:
        dictionary[str(line).strip('\n')] = str(line).strip('\n')
    print("Dictionary loaded. Proceeding with the search...")

    # Begin initial tree construction
    noRepeatNodes = {}
    assembleTree(initialState, noRepeatNodes, dictionary, goalState)

    # Call assembleTree again on each child so that we don't only get one possible path (as opposed to
    # calling it recursively, where only the first child will ever have child nodes).
    for child in initialState.childNodes:
        assembleTree(child, noRepeatNodes, dictionary, goalState)

    # Conduct A* search from the starting node, find total cost to get to the goal
    pathToGoal = aStar(initialState, goalState, noRepeatNodes, dictionary)
    pathToGoalStr = []
    pathLen = len(pathToGoal)
    totalCostToGoal = pathToGoal[pathLen - 1].totalCost

    # Convert result to strings
    for node in pathToGoal:
        pathToGoalStr.append(node.word)
    print("Path found, total cost is: " + str(totalCostToGoal))
    print(pathToGoalStr)
