# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, Board
import copy, sys


# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!



def fill_full_dict():
        board_dict = {}
        for i in range(0, 7):
            for j in range(0, 7):
                board_dict[HexPos(i, j)] = None
        return board_dict

def calc_heuristics(player: PlayerColor, board: Board, action: Action):
    temp_board = copy.deepcopy(board)
    temp_board.apply_action(action)
    self_k = self_n = oppo_k = oppo_n = 0
    for pos, state in temp_board._state.items():
        if state.player == player:
            self_n += 1
            self_k += state.power
        else:
            oppo_n += 1
            oppo_k += state.power
    temp_board.undo_action()
    return (oppo_k ** oppo_n) / (self_k ** self_n)

def possible_actions(player_colour: PlayerColor, board: Board):
    b_dict = board._state
    spawn_dict = fill_full_dict()
    spread_dict = []
    action_list = []
    colour = player_colour
    for pos, state in b_dict.items():
        del spawn_dict[pos]
        if state.player == colour:
            spread_dict.append(pos)
    
    for i in spread_dict:
        for dir in HexDir:
            action_list.append(SpreadAction(i, dir))
    
    for i in spawn_dict.keys():
        action_list.append(SpawnAction(i))

    return action_list

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
    
    def greedy_select(self):
        h = sys.maxsize
        action_list = possible_actions(self._color, self.board)
        final_action = action_list[0]
        for action in action_list:
            curr_h = calc_heuristics(self._color, self.board, action)
            if curr_h < h:
                h = curr_h
                final_action = action
        return final_action

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
                    return self.greedy_select()
                return SpawnAction(HexPos(3, 3))
            case PlayerColor.BLUE:
                # This is going to be invalid... BLUE never spawned!
                if self.board._history != None:
                    return self.greedy_select()
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