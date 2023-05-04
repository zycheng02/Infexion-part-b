# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, Board
import copy, sys, random
import math;

# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!
class Node:
    def __init__(self, board, action=None, parent=None):
        self.board = board
        self.action = action
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0

    def is_terminal(self):
        # gameover includes draw
        return self.board.game_over
    # selection to find best UCB child
    def selection(self):
        C =1
        best_score = -math.inf
        best_child = None
        for child in self.children:
            # UCB
            score = child.wins / child.visits + C * math.sqrt(math.log(self.visits) / child.visits)
            # iteratively find best child
            if score > best_score:
                best_score = score
                best_child = child
        return best_child
        
    # expansion
    def expansion(self):
        random_action = possible_actions(self.board)
        #choose random action and create child node for action
        next_board = next_board_nonmut(self.board, random_action)
        child_node = Node(next_board, random_action, self)
        self.children.append(child_node)

        return child_node
    
    # playout
    def playout(self, board):
    

        # play (take turns between us n opponent)
        next_move = possible_actions(board)
        board.apply_action(next_move)

        # check if finished
        if not board.game_over:
            self.playout(board)

        # if simulation has reached end state
        return board.winner_color
    
    # backpropagation
    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)

# returns copy of board with action applied 
def next_board_nonmut(board, action):
    next_board = copy.deepcopy(board)
    next_board.apply_action(action)
    return next_board

# (populate full board allowed for spawn)
def fill_full_dict():
        board_dict = {}
        for i in range(0, 7):
            for j in range(0, 7):
                board_dict[HexPos(i, j)] = None
        return board_dict

def possible_actions(board):
    b_dict = board._state
    # dictionary of spawn pos allowed 
    spawn_dict = fill_full_dict()
    spread_dict = []
    action_list = []
    
    for pos, state in b_dict.items():
        # check off already occupied positions 
        del spawn_dict[pos]
        # if ur piece, (state.player is color of piece) can spread
        if state.player == board.turn_color:

            # print(self._color)
            spread_dict.append(pos)
    
    for i in spawn_dict.keys():
        action_list.append(SpawnAction(i))
    

    for i in spread_dict:
        for dir in HexDir:
            # print(i)
            # print("-------------")
            action_list.append(SpreadAction(i, dir))
    return random.choice(action_list)

class Agent:
    def monte_carlo_tree_search(initial_state, max_iterations=1000):
        root =  Node(initial_state.board)
        # print(initial_state.board.render())
        
        for x in range(max_iterations):
            current_node = root
            while not current_node.is_terminal() and current_node.children:
                current_node = current_node.selection()
            if not current_node.is_terminal():
                current_node = current_node.expansion()
                # print(current_node.board.render())
                # if current_node.children:
                #     print("expansion worked")
                #     current_node = random.choice(current_node.children)
            simboard= copy.deepcopy(current_node.board)
            color = current_node.playout(simboard)
            result =0
            if color == initial_state._color:
                result =1
            else: result =0
            current_node.backpropagate(result)

        # choose child most simulated as next move as most confident
        best_child = max(root.children, key=lambda x: x.visits)
        return best_child.action

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")
        self.board = Board()

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        match self._color:
            case PlayerColor.RED:
                if self.board.turn_count > 1:
                    # print(self.board.render())
                    return self.monte_carlo_tree_search(50)
                return SpawnAction(HexPos(3, 3))
            case PlayerColor.BLUE:
                # This is going to be invalid... BLUE never spawned!
                if self.board.turn_count > 1:
                    return self.monte_carlo_tree_search(50)
                return SpawnAction(HexPos(3, 4))
                return SpreadAction(HexPos(3, 3), HexDir.Up)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        # if self._color != color:
        # print(self.board.__getitem__(HexPos(0,0)))
        # update board used by agent in algo
        self.board.apply_action(action)
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass