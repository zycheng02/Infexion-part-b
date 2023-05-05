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

def fill_full_dict():
        board_dict = {}
        for i in range(0, 7):
            for j in range(0, 7):
                board_dict[HexPos(i, j)] = None
        return board_dict

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

def possible_actions(player_colour: PlayerColor, board: Board):
    b_dict = board._state
    spawn_dict = fill_full_dict()
    spread_dict = []
    action_list = []
    colour = player_colour
    for pos, state in b_dict.items():
        if pos in spawn_dict:
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
            action_list.append(SpreadAction(i, dir))
    
    for i in spawn_dict.keys():
        action_list.append(SpawnAction(i))

    return action_list

def ini_spawn(board: Board):
    action_list = []
    b_dict = board._state
    spawn_dict = fill_full_dict()
    for pos, state in b_dict.items():
        if pos in spawn_dict:
            del spawn_dict[pos]
        for dir in HexDir:
            temp = pos
            temp = temp.__add__(dir)
            if temp in spawn_dict:
                del spawn_dict[temp]

    for i in spawn_dict.keys():
        action_list.append(SpawnAction(i))

    return random.choice(action_list)

def build_leaf(root: Node, layer):
    temp_board = copy.deepcopy(root.board)
    curr_player = root.board.turn_color
    # if layer % 2 != 0:
    #     if temp_board.turn_color == PlayerColor.RED:
    #         temp_board.turn_color = PlayerColor.BLUE
    #         curr_player = PlayerColor.BLUE
    #     else:
    #         temp_board.turn_color = PlayerColor.RED
    #         curr_player = PlayerColor.RED
    action_list = possible_actions(curr_player, temp_board)
    children_list = []
    min_cost = sys.maxsize
    for action in action_list:
        curr_board = copy.deepcopy(temp_board)
        curr_board.apply_action(action)
        if layer == 0:
            h = calc_heuristics(curr_player, curr_board)
            if h > min_cost:
                continue
            min_cost = min(min_cost, h)
        curr_node = Node(curr_board, action)
        children_list.append(curr_node)
    root.next_steps = children_list
    
def minimax(root: Node, depth, alpha, beta, max_round):
    if depth >= TREE_DEPTH:
        root.chosen_cost = calc_heuristics(root.board.turn_color, root.board)
        return
    
    if max_round:
        max_cost = -1
        for child in root.next_steps:
            minimax(child, depth+1, alpha, beta, False)
            if child.chosen_cost > max_cost:
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
            if child.chosen_cost < min_cost:
                min_cost = child.chosen_cost
                root.chosen_action = child.action
            beta = min(beta, child.chosen_cost)
            if beta <= alpha:
                break
        root.chosen_cost = min_cost
        return

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
    return root.chosen_action

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

    # def calc_heuristics(self, action: Action):
    #     temp_board = copy.deepcopy(self.board)
    #     temp_board.apply_action(action)
    #     oppo = [pos for pos in temp_board._state.keys() if temp_board._state[pos].player != self._color]
    #     if len(oppo) == 1:
    #         return 1
    #     for op in oppo:
    #         for dir in HexDir:
    #             temp = op
    #             for i in range(6):
    #                 temp.__add__(dir)
    #                 if temp in oppo:
    #                     oppo.remove(temp)
    #     temp_board.undo_action()
    #     num_lines = len(oppo)
    #     return num_lines

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
                # This is going to be invalid... BLUE never spawned!
                # if self.board.turn_count < 10:
                #     return ini_spawn(self.board)
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