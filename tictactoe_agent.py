import sys
import os
import time

class Board:
    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.board = [[' ' for _ in range(n)] for _ in range(n)]
        
    def print(self):
        
        for row in self.board:
            print('|'.join(row))
        print("")

    def is_full(self):
        return all(' ' not in row for row in self.board)
    
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
        
    def check_end(self, player):
        if self.is_full():
            return "draw"
        for i in range(self.n):
            for j in range(self.n):
                if self.check_line(i, j, 1, 0, player) or \
                   self.check_line(i, j, 0, 1, player) or \
                   self.check_line(i, j, 1, 1, player) or \
                   self.check_line(i, j, 1, -1, player):
                    return "win"
        return "continue"
    
    def make_move(self, row, col, player):
        if self.board[row][col] == ' ':
            self.board[row][col] = player
            return True
        return False
    
    def undo_move(self, row, col):
        self.board[row][col] = ' '

def alpha_beta_search(board, depth, alpha, beta, player, k, maximizing):
    opponent = 'x' if player == 'o' else 'o'
    state = board.check_end(player)
    if state == "win":
        return 1 if maximizing else -1
    elif state == "draw":
        return 0
    if depth == 0:
        return 0

    if maximizing:
        max_eval = float('-inf')
        for i in range(board.n):
            for j in range(board.n):
                if board.board[i][j] == ' ':
                    board.make_move(i, j, player)
                    eval = alpha_beta_search(board, depth - 1, alpha, beta, player, k, False)
                    board.undo_move(i, j)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval
    else:
        min_eval = float('inf')
        for i in range(board.n):
            for j in range(board.n):
                if board.board[i][j] == ' ':
                    board.make_move(i, j, opponent)
                    eval = alpha_beta_search(board, depth - 1, alpha, beta, player, k, True)
                    board.undo_move(i, j)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return min_eval
    
def get_ordered_moves(board):
    center = (board.n // 2, board.n // 2)
    
    def distance_to_center(row, col):
        return abs(center[0] - row) + abs(center[1] - col)
    
    empty_cells = [(i, j) for i in range(board.n) for j in range(board.n) if board.board[i][j] == ' ']
    empty_cells.sort(key=lambda cell: distance_to_center(*cell))  # Sort by proximity to center
    return empty_cells

def get_best_move(board, player, k, depth=4):
    start_time = time.time()
    
    best_move = None
    best_value = float('-inf') if player == 'x' else float('inf')

    ordered_moves = get_ordered_moves(board)
    for row, col in ordered_moves:
        board.make_move(row, col, player)
        move_value = alpha_beta_search(board, depth, float('-inf'), float('inf'), player, k, player == 'x')
        board.undo_move(row, col)
        
        if player == 'x' and move_value > best_value:
            best_value = move_value
            best_move = (row, col)
        elif player == 'o' and move_value < best_value:
            best_value = move_value
            best_move = (row, col)
    
    gap = time.time() - start_time
    print(best_move, ": ", "{:.3f}".format(gap), "s")
    return best_move  
    

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
    with open(filename, 'a+') as f:  
        col_letter = chr(ord('a') + col)
        move_str = f"{player}{row + 1}{col_letter}\n"
        f.write(move_str)

def main():
    n = int(sys.argv[1])
    k = int(sys.argv[2])
    player = sys.argv[3] # x first, o second
    
    # Initialize board
    board = Board(n, k)
    x_file = "xmoves.txt"
    o_file = "omoves.txt"
    move_file = x_file if player == 'x' else o_file
    opponent_file = o_file if player == 'x' else x_file
    opponent = 'o' if player == 'x' else 'x'
        
    round_number = 1  # Start at round 1

    if player == 'x':
        while True:
            # Get best move using alpha-beta pruning
            move = get_best_move(board, player, k)
            if move:
                row, col = move
                board.make_move(row, col, player)
                # board.print()
                write_move(move_file, player, row, col)

            result = board.check_end(player)
            if result == "win":
                print("win")
                break
            elif result == "draw":
                print("draw")
                break

            # Wait for opponent's move
            _, row, col = read_move(opponent_file, round_number)
            if row != -1 and col != -1:
                board.make_move(row, col, opponent)
                # board.print()

            result = board.check_end(opponent)
            if result == "win":
                print("lose")
                break
            elif result == "draw":
                print("draw")
                break

            round_number += 1  # Increment round

    else:
        while True:
            # Wait for opponent's move
            _, row, col = read_move(opponent_file, round_number)
            if row != -1 and col != -1:
                board.make_move(row, col, opponent)
                # board.print()

            result = board.check_end(opponent)
            if result == "win":
                print("lose")
                break
            elif result == "draw":
                print("draw")
                break

            move = get_best_move(board, player, k)
            if move:
                row, col = move
                board.make_move(row, col, player)
                # board.print()
                write_move(move_file, player, row, col)

            result = board.check_end(player)
            if result == "win":
                print("win")
                break
            elif result == "draw":
                print("draw")
                break

            round_number += 1  
    board.print()

if __name__ == "__main__":
    main()
