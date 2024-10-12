import sys
import os
import time
import random
import math

class Board:
    def __init__(self, n, k, player):
        self.n = n  # Grid size
        self.k = k  
        self.board = [[' ' for _ in range(n)] for _ in range(n)]
        self.player = player

    def make_move(self, row, col, player=None):
        if not player:
            player = self.player
        self.board[row][col] = player


    def check_line(self, i, j, dr, dc, player):
        count = 0
        for _ in range(self.k):
            if 0 <= i < self.n and 0 <= j < self.n and self.board[i][j] == player:
                count += 1
            else:
                break
            i += dr
            j += dc
        return count == self.k

    def check_end(self):
        opponent = 'x' if self.player == 'o' else 'o'
        for i in range(self.n):
            for j in range(self.n):
                if self.check_line(i, j, 1, 0, self.player) or self.check_line(i, j, 0, 1, self.player) or \
                   self.check_line(i, j, 1, 1, self.player) or self.check_line(i, j, 1, -1, self.player):
                    # self.print()
                    return self.player
                if self.check_line(i, j, 1, 0, opponent) or self.check_line(i, j, 0, 1, opponent) or \
                   self.check_line(i, j, 1, 1, opponent) or self.check_line(i, j, 1, -1, opponent):
                    return opponent
        if all(self.board[i][j] != ' ' for i in range(self.n) for j in range(self.n)):
            return "draw"
        return "continue"

    def get_legal_moves(self):
        center = (self.n // 2, self.n // 2)
    
        def distance_to_center(row, col):
            return abs(center[0] - row) + abs(center[1] - col)
        
        moves = [(i, j) for i in range(self.n) for j in range(self.n) if self.board[i][j] == ' ']
        moves.sort(key=lambda cell: distance_to_center(*cell))
        return moves
    
    def get_smart_move(self):
        possible_moves = self.get_legal_moves()  
        for move in possible_moves:
            self.make_move(move[0], move[1], self.player)
            if self.check_end() == self.player:
                self.make_move(move[0], move[1], ' ')  
                return move  
            self.make_move(move[0], move[1], ' ')
            
        
        opponent = 'o' if self.player == 'x' else 'x'
        
        for move in possible_moves:
            self.make_move(move[0], move[1], opponent)
            if self.check_end() == opponent:
                self.make_move(move[0], move[1], ' ')  # Undo the move after checking
                return move  
            self.make_move(move[0], move[1], ' ')

        return None

    def copy(self):
        new_board = Board(self.n, self.k, self.player)
        new_board.board = [row[:] for row in self.board]
        return new_board

    def print(self):
        for row in self.board:
            print(' '.join([cell if cell != ' ' else '.' for cell in row]))
        print("")


class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = board.copy()  
        self.parent = parent  
        self.move = move  
        self.children = []  
        self.wins = 0  
        self.visits = 0  
        self.untried_moves = self.board.get_legal_moves()  

    def expand(self):
        move = self.untried_moves.pop()
        next_board = self.board.copy()
        next_board.make_move(move[0], move[1])
        child_node = Node(next_board, self, move)
        self.children.append(child_node)
        return child_node

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    # def best_child(self, exploration_weight=0.5):
    #     """Use UCB1 to select the best child node."""
    #     choices_weights = [
    #         (child.wins / child.visits) + exploration_weight * math.sqrt(2 * math.log(self.visits) / child.visits)
    #         for child in self.children
    #     ]
    #     return self.children[choices_weights.index(max(choices_weights))]
    

    def best_child(self, exploration_weight=0, previous_move=None):
        def proximity_bias_heuristic(current_move, previous_move):
            return abs(current_move[0] - previous_move[0]) + abs(current_move[1] - previous_move[1])
        
        choices_weights = []

        for child in self.children:
            ucb1_value = (child.wins / child.visits) + exploration_weight * math.sqrt(2 * math.log(self.visits) / child.visits)

            # If previous move is available, apply proximity bias
            if previous_move:
                proximity_bias = -proximity_bias_heuristic(child.move, previous_move)  # Closer moves get higher priority
                ucb1_value += proximity_bias

            choices_weights.append(ucb1_value)

        return self.children[choices_weights.index(max(choices_weights))]

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)

    def is_terminal(self):
        return self.board.check_end() != "continue"

    def rollout(self):
        current_rollout_board = self.board.copy()
        current_player = self.board.player
        opponent = 'x' if current_player == 'o' else 'o'
        players = (current_player, opponent)
        
        cnt = 0
        
        while current_rollout_board.check_end() == "continue":
            possible_moves = current_rollout_board.get_legal_moves()
            move = random.choice(possible_moves)
            current_rollout_board.make_move(move[0], move[1], players[cnt % 2])
            # current_player = switch_player(current_player)
            cnt += 1
            # current_rollout_board.print()
            
        result = current_rollout_board.check_end()
        if result == self.board.player:
            return 1
        elif result == 'draw':
            return 0
        else: 
            return -2
    

class MonteCarloTreeSearch:
    def __init__(self, board):
        self.root = Node(board)

    def best_move(self, max_time=5.0):
        start_time = time.time()
        # cnt = 0
        smart_move = self.root.board.get_smart_move()
        if smart_move:
            print(smart_move, ": ", "{:.3f}".format(time.time() - start_time), "s")
            return smart_move
        while time.time() < start_time + max_time:
            node = self.select_node()
            if not node.is_terminal():
                node = node.expand()
            result = node.rollout()
            # print(result)
            node.backpropagate(result)
            # cnt += 1
        # print("count:", cnt)
        t = time.time() - start_time
        print(self.root.best_child().move, ": ", "{:.3f}".format(t), "s")
        return self.root.best_child().move

    def select_node(self):
        node = self.root
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node
            else:
                node = node.best_child()
        return node


def read_move(filename, round_number):
    while not os.path.exists(filename):
        time.sleep(0.1)
    lines = []
    while True:
        with open(filename, 'r') as f:
            lines = f.readlines()
            if round_number > len(lines):
                time.sleep(1)
            else:
                break
    move = lines[round_number - 1].strip()
    player = move[0]
    row = int(move[1]) - 1
    col = ord(move[2]) - ord('a')
    return player, row, col


def write_move(filename, player, row, col):
    with open(filename, 'a') as f:
        col_letter = chr(ord('a') + col)
        move_str = f"{player}{row + 1}{col_letter}\n"
        f.write(move_str)


def main():
    n = int(sys.argv[1])
    k = int(sys.argv[2])
    player = sys.argv[3]
    # print("hi")
    board = Board(n, k, player)
    x_file = "xmoves.txt"
    o_file = "omoves.txt"
    move_file = x_file if player == 'x' else o_file
    opponent_file = o_file if player == 'x' else x_file
    opponent = 'o' if player == 'x' else 'x'
    
    round_number = 1
    if player == 'x':
        while True:
            mcts = MonteCarloTreeSearch(board)
            move = mcts.best_move()
            if move:
                row, col = move
                board.make_move(row, col, player)
                write_move(move_file, player, row, col)

            result = board.check_end()
            if result != "continue":
                # print(result)
                break

            _, row, col = read_move(opponent_file, round_number)
            board.make_move(row, col, opponent)

            result = board.check_end()
            if result != "continue":
                # print(result)
                break

            round_number += 1
    else:
        while True:
            _, row, col = read_move(opponent_file, round_number)
            board.make_move(row, col, opponent)
            # board.print()
            result = board.check_end()
            if result != "continue":
                # print(result)
                break
            
            mcts = MonteCarloTreeSearch(board)
            move = mcts.best_move()
            if move:
                row, col = move
                board.make_move(row, col, player)
                write_move(move_file, player, row, col)

            result = board.check_end()
            if result != "continue":
                # print(result)
                break

            round_number += 1
    board.print()


if __name__ == "__main__":
    main()

