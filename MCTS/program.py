# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, Board
import copy, sys, random
import math, heapq;

# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!
class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._index = 0

    def push(self, item, priority):
        heapq.heappush(self._heap, (-priority, self._index, item))
        self._index += 1
    def pop(self):
        item = heapq.heappop(self._heap)[-1]
        return item

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
    # if oppo_n == 0:
    #     return 0
    # if self_n == 0:
    #     return sys.maxsize
    
    return (oppo_k ** oppo_n) / (self_k ** self_n)

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
        C =1.4
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

        #choose random action and create child node for action
        action_list = possible_actions(self.board)
        action_h_list = PriorityQueue()
        board = self.board
        next_move = None

        for action in action_list:
            board.apply_action(action) 
            # can maybe remove game winner checker below? if heuristic responds to win as it should
            if board.game_over:
                action_h_list.push(action, calc_heuristics(board.turn_color, board))
                board.undo_action()
                break
            else: 
                action_h_list.push(action, calc_heuristics(board.turn_color, board))
            board.undo_action()
            
        top_child = None
        if next_move == None:
            # expand for x no of nodes 
            for _ in range(3):
                next_move = action_h_list.pop()
                next_board = next_board_nonmut(self.board, next_move)
                child_node = Node(next_board, next_move, self)
                child_node.visits = 1
                child_node.wins = 0.2
                self.children.append(child_node)
                if _ == 0:
                    print(next_board.render())
                    print("uhhh")
                    top_child = child_node
        # only returns best move as choice of playout
        return top_child
    
    # playout
    def playout(self, board):
    

        # play (take turns between us n opponent)
        action_list = possible_actions(board)
        action_h_list = PriorityQueue()
        next_move = None
        for action in action_list:
            board.apply_action(action) 
            action_h_list.push(action, calc_heuristics(board.turn_color, board))
            board.undo_action()
        
        # check if finished
        if not board.game_over:
            next_move = action_h_list.pop()
            board.apply_action(next_move)
            # print(board.turn_count)
            self.playout(board)

        # if simulation has reached end state
        else:
            # print(board.winner_color)
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
    return action_list

class Agent:
    def monte_carlo_tree_search(initial_state, max_iterations=1000):
        root =  Node(initial_state.board)
        # print(initial_state.board.render())
        
        for x in range(max_iterations):
            current_node = root
            # select best leaf node according to ucb
            while not current_node.is_terminal() and current_node.children:
                current_node = current_node.selection()
            # expand selected node
            if not current_node.is_terminal():
                current_node = current_node.expansion()
                # print(current_node.board.render())
                # if current_node.children:
                #     print("expansion worked")
                #     current_node = random.choice(current_node.children)
            # select new expanded child node to playout
            simboard= copy.deepcopy(current_node.board)
            color = current_node.playout(simboard)
            result =0
            if color == initial_state._color:
                result =1
            else: result =0
            current_node.backpropagate(result)

        # choose child most simulated as next move as most confident
        [print(x.action) for x in root.children]
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
                    return self.monte_carlo_tree_search(200)
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