# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, Board
import copy, sys, random
from dataclasses import dataclass

TREE_DEPTH = 2


# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!

@dataclass
class Node:
    board: Board
    action: Action
    next_steps: list = None
    chosen_action: Action = None
    chosen_cost: float = None

# fill a dictionary with all of the possible coordinates in the game 
def fill_full_dict():
        board_dict = {}
        for i in range(0, 7):
            for j in range(0, 7):
                board_dict[HexPos(i, j)] = None
        return board_dict

# Calculate heuristics based on the ratio between the pieces of the current player and
# that of the opponents
def calc_heuristics(player: PlayerColor, board: Board):
    temp_board = copy.deepcopy(board)
    self_k = self_n = oppo_k = oppo_n = 0
    for pos, state in temp_board._state.items():
        if state.player == player:
            self_n += 1
            self_k += state.power
        else:
            oppo_n += 1
            oppo_k += state.power
    if oppo_n == 0:
        return 0
    if self_n == 0:
        return sys.maxsize
    
    return (oppo_k ** oppo_n) / (self_k ** self_n)

def diff(board: Board, player: PlayerColor):
    self = [pos for pos in board._state.keys() if board._state[pos].player == player]
    if player == PlayerColor.RED:
        op_c = PlayerColor.BLUE
    else:
        op_c = PlayerColor.RED
    oppo = [pos for pos in board._state.keys() if board._state[pos].player == op_c]
    return len(oppo) - len(self)

# Get all of the possible actions for the given player on the current board
def possible_actions(player_colour: PlayerColor, board: Board):
    b_dict = board._state
    spawn_dict = fill_full_dict()
    spread_dict = []
    action_list = []
    colour = player_colour
    for pos, state in b_dict.items():
        if pos in spawn_dict:
            # bug fix, need to check whether position is occupied through player color,
            # because empty space still has entry in b_dict.items()
            if state.player != None:
                del spawn_dict[pos]

        if state.player == colour:
            spread_dict.append(pos)
        else:
            if board.turn_count < 10:
                for dir in HexDir:
                    temp = pos
                    temp = temp.__add__(dir)
                    if temp in spawn_dict:
                        del spawn_dict[temp]
    
    for i in spread_dict:
        for dir in HexDir:
            cpy = copy.deepcopy(board)
            try:
                cpy.apply_action(SpreadAction(i, dir))
            except:
                continue
            else:
                action_list.append(SpreadAction(i, dir))
    
    
    for i in spawn_dict.keys():
        cpy = copy.deepcopy(board)
        try:
            cpy.apply_action(SpawnAction(i))
        except:
            continue
        else:
            action_list.append(SpawnAction(i))

    # print(action_list)
    return action_list

# build the given note with its possible actions
def build_leaf(root: Node, layer):
    temp_board = copy.deepcopy(root.board)
    curr_player = root.board.turn_color
    action_list = possible_actions(curr_player, temp_board)
    children_list = []
    min_cost = sys.maxsize
    # create children node for each action
    for action in action_list:
        curr_board = copy.deepcopy(temp_board)
        curr_board.apply_action(action)
        # if it's the first layer, only add children nodes that has minimum
        # heuristics to reduce tree size
        if layer == 0:
            h = calc_heuristics(curr_player, curr_board)
            if h > min_cost:
                continue
            min_cost = min(min_cost, h)
        curr_node = Node(curr_board, action)
        children_list.append(curr_node)
    root.next_steps = children_list
    
# minimax decision algorithm with alpha-beta pruning
def minimax(root: Node, depth, alpha, beta, max_round):
    if depth >= TREE_DEPTH:
        root.chosen_cost = calc_heuristics(root.board.turn_color, root.board)
        return
    
    if max_round:
        max_cost = -1
        for child in root.next_steps:
            minimax(child, depth+1, alpha, beta, False)
            if child.chosen_cost != None:
                if child.chosen_cost >= max_cost:
                    max_cost = child.chosen_cost
                    root.chosen_action = child.action
                alpha = max(alpha, max_cost)
            if beta <= alpha:
                break
        root.chosen_cost = max_cost
        return
    else:
        min_cost = sys.maxsize
        for child in root.next_steps:
            minimax(child, depth+1, alpha, beta, True)
            if min_cost == sys.maxsize:
                min_cost = child.chosen_cost
            if child.chosen_cost != None:
                if child.chosen_cost <= min_cost:
                    min_cost = child.chosen_cost
                    root.chosen_action = child.action
                beta = min(beta, child.chosen_cost)
            if beta <= alpha:
                break
        root.chosen_cost = min_cost
        return

# build possible action tree
def fill_tree(root: Node, layer):
    if layer >= TREE_DEPTH:
        return
        
    build_leaf(root, layer)

    for child in root.next_steps:
        fill_tree(child, layer+1)

def next_step_select(board: Board):
    root = Node(board, None)
    fill_tree(root, 0)
    # print('FINISHED TREE')
    minimax(root, 0, -1, sys.maxsize, False)
    if root.chosen_action:
        return root.chosen_action
    return random.choice(root.next_steps)

def greedy_select(colour: PlayerColor, board: Board):
    h = sys.maxsize
    action_list = possible_actions(colour, board)
    final_action = action_list[0]
    for action in action_list:
        temp_board = copy.deepcopy(board)
        temp_board.apply_action(action)
        curr_h = calc_heuristics(colour, temp_board)
        if curr_h < h:
            h = curr_h
            final_action = action
    return final_action

class Agent:

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
                if self.board._history != None:
                    return next_step_select(self.board)
                return SpawnAction(HexPos(3, 3))
            case PlayerColor.BLUE:
                if self.board._history != None:
                    return next_step_select(self.board)
                return SpawnAction(HexPos(3, 4))
                return SpreadAction(HexPos(3, 3), HexDir.Up)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        # if self._color != color:
        # print(self.board.__getitem__(HexPos(0,0)))
        self.board.apply_action(action)
        match action:
            case SpawnAction(cell):
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass