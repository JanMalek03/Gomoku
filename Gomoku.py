import tkinter as tk
from tkinter import ttk
from GomokuGUI import GomokuGUI
from GomokuGUI import Color

BOARD_SIZE = 15


class Gomoku:
    def __init__(self):
        self.initialize_game()


    def initialize_game(self):
        self.board = [[Color.NONE] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.player_color = Color.BLACK
        self.game_over = False
        self.empty_positions = {(i, j) for i in range(5, 10) for j in range(5, 10)}
        self.last_play = None


    def set_gui(self, gui):
        self.gui = gui


    def is_winning_move(self, color, x, y, winning_positions = None):
        if winning_positions is None:
            winning_positions = []

        multiplyers = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in multiplyers:
            if self.check_line(color, x, y, dx, dy, winning_positions):
                return True

        if self.empty_positions == set():
            return "DRAW"

        return False


    def check_line(self, color, x, y, dx, dy, winning_positions):
        consecutive_count = 0

        for i in range(-5, 6):
            nx, ny = x + i * dx, y + i * dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                if self.board[nx][ny] == color:
                    consecutive_count += 1
                    winning_positions.append((nx, ny))
                else:
                    if consecutive_count == 5:
                        return True
                    consecutive_count = 0
                    winning_positions.clear()
            else:
                if consecutive_count == 5:
                    return True
                consecutive_count = 0
                winning_positions.clear()

        if consecutive_count == 5:
            return True
        return False


    def make_move(self, x, y, color, initial=False):
        if not self.is_valid(x, y) or self.game_over:
            return True
        assert self.board[x][y] == Color.NONE

        if self.last_play:
            last_x, last_y = self.last_play
            last_color = self.board[last_x][last_y]
            self.draw_circle(last_x, last_y, last_color)
        self.last_play = (x, y)

        self.board[x][y] = color
        self.add_empty_positions(x, y)
        if (x, y) in self.empty_positions:
            self.empty_positions.remove((x, y))
        self.draw_circle(x, y, color)
        if not initial:
            self.gui.place_dot(x, y)

        winning_positions = []
        result = self.is_winning_move(color, x, y, winning_positions)
        if result:
            if result == "DRAW":
                print("It's a DRAW!")
            else:
                self.gui.highlight_winning_cells(winning_positions)
                print("PLAYER " + self.color_to_string(color) + " WON!!!")
            self.game_over = True
            self.gui.game_over()

        return False


    def add_empty_positions(self, x, y):
        for i in range(x - 2, x + 2):
            for j in range(y - 2, y + 2):
                if i >= 0 and j >= 0 and i < BOARD_SIZE and j < BOARD_SIZE:
                    if self.is_valid(i, j):
                        self.empty_positions.add((i, j))


    def draw_circle(self, x, y, color):
        self.gui.place_circle(x, y, self.color_to_string(color))


    def ai_make_move(self):
        if self.game_over:
            return

        ai_color = self.get_opposite_color(self.player_color)

        best_x, best_y = self.try_basic_best_moves(ai_color)
        if (best_x is not None and best_y is not None):
            print()
            print(best_x, best_y)
            self.make_move(best_x, best_y, ai_color)
            return

        best_score = float('-inf')
        best_move = None

        for move in self.empty_positions:
            x, y = move
            self.board[x][y] = ai_color
            was_in_empty = False
            if (x, y) in self.empty_positions:
                was_in_empty = True
                self.empty_positions.remove((x, y))
            score = self.minimax(2, float('-inf'), float('inf'), True)
            self.board[x][y] = Color.NONE
            if was_in_empty:
                self.empty_positions.add((x, y))

            if score > best_score:
                best_score = score
                best_move = move

        assert best_move
        print()
        print(best_move[0], best_move[1])
        self.make_move(best_move[0], best_move[1], ai_color)


    def try_basic_best_moves(self, color):
        opposite_color = self.get_opposite_color(color)
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if (self.board[x][y] != Color.NONE):
                    continue

                if (self.simulate_and_test(x, y, color)):
                    return x, y
                if (self.simulate_and_test(x, y, opposite_color)):
                    return x, y


        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if (self.board[x][y] != Color.NONE):
                    continue

                if (self.dangerous_trio(x, y, color)):
                    return x, y
                if (self.dangerous_trio(x, y, opposite_color)):
                    return x, y

        return None, None


    def simulate_and_test(self, x, y, color):
        self.board[x][y] = color
        was_in_empty = False
        if (x, y) in self.empty_positions:
            was_in_empty = True
            self.empty_positions.remove((x, y))
        result = self.is_winning_move(color, x, y)
        self.board[x][y] = Color.NONE
        if (was_in_empty):
            self.empty_positions.add((x, y))
        return result


    def dangerous_trio(self, x, y, color):
        multiplyers = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in multiplyers:
            for i in range(1, 5):
                new_x = x + i * dx
                new_y = y + i * dy
                if not self.in_range(new_x, new_y):
                    break
                if i != 4 and self.board[new_x][new_y] != self.get_opposite_color(color):
                    break
                if i == 4 and self.board[new_x][new_y] == Color.NONE:
                    return True

            for i in range(-2, 4):
                new_x = x + i * dx
                new_y = y + i * dy
                if not self.in_range(new_x, new_y):
                    break
                if i == -2 and self.board[new_x][new_y] != Color.NONE:
                    break
                if (i == -1 or i == 1 or i == 2) and self.board[new_x][new_y] != self.get_opposite_color(color):
                    break
                if i == 3 and self.board[new_x][new_y] == Color.NONE:
                    return True

            for i in range(-3, 3):
                new_x = x + i * dx
                new_y = y + i * dy
                if not self.in_range(new_x, new_y):
                    break
                if i == -3 and self.board[new_x][new_y] != Color.NONE:
                    break
                if (i == -2 or i == -1 or i == 1) and self.board[new_x][new_y] != self.get_opposite_color(color):
                    break
                if i == 2 and self.board[new_x][new_y] == Color.NONE:
                    return True

        return False


    def in_range(self, x, y):
        return (x >= 0 and y >= 0 and x < BOARD_SIZE and y < BOARD_SIZE)


    def minimax(self, depth, alpha, beta, maximizing_player):
        ai_color = self.get_opposite_color(self.player_color)

        if depth == 0 or self.game_over:
            return self.evaluate_position(ai_color)

        if maximizing_player:
            max_eval = float('-inf')
            for move in list(self.empty_positions):
                i, j = move
                self.board[i][j] = ai_color
                was_in_empty = False
                if (i, j) in self.empty_positions:
                    was_in_empty = True
                    self.empty_positions.remove((i, j))
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.board[i][j] = Color.NONE
                if was_in_empty:
                    self.empty_positions.add((i, j))
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in list(self.empty_positions):
                i, j = move
                self.board[i][j] = self.player_color
                was_in_empty = False
                if (i, j) in self.empty_positions:
                    was_in_empty = True
                    self.empty_positions.remove((i, j))
                eval = self.minimax(depth - 1, alpha, beta, True)
                self.board[i][j] = Color.NONE
                if was_in_empty:
                    self.empty_positions.add((i, j))
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval


    def evaluate_position(self, color, calc_proxi = True):
        score = 0
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.board[x][y] == color:
                    score += self.count_connected(color, x, y)
                    score += self.trio_bonus(color, x, y)
                    if calc_proxi:
                        score += self.edge_proximity_bonus(x, y)
        return score


    def count_connected(self, color, x, y):
        connected = 0
        for dx, dy in [(0, 1), (1, 0), (1, 1), (-1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.board[nx][ny] == color:
                connected += 1
        return connected


    def trio_bonus(self, color, x, y):
        trio_counter = 0
        for dx, dy in [(0, 1), (1, 0), (1, 1), (-1, 1)]:
            stone_count = 1
            empty_count = 0
            for i in range(1, 4):
                nx, ny = x + i * dx, y + i * dy
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                    if self.board[nx][ny] == color:
                        stone_count += 1
                    elif self.board[nx][ny] == Color.NONE:
                        empty_count += 1
                    else:
                        break
                else:
                    break

            if stone_count == 3 and empty_count > 0:
                trio_counter += 1

        return trio_counter


    def edge_proximity_bonus(self, x, y):
        distance_from_center = abs(x - BOARD_SIZE // 2) + abs(y - BOARD_SIZE // 2)
        return 2 ** (BOARD_SIZE // 2 - distance_from_center)


    def get_opposite_color(self, color):
        if color == Color.BLACK:
            return Color.WHITE
        else:
            return Color.BLACK


    #TODO: musel jsem oddelat pocitani proxi, ale mozna by to tam nejak chtelo
    def evaluate_starting(self, color):
        if color == Color.BLACK:
            return self.evaluate_position(color, calc_proxi=False)

        best = 0
        best_move = (-1, -1)

        for move in list(self.empty_positions):
            i, j = move
            self.board[i][j] = color
            eval = self.evaluate_position(color, calc_proxi=False)
            self.board[i][j] = Color.NONE
            if (eval > best):
                best = eval
                best_move = (i, j)

        return best


    def is_valid(self, x, y):
        return self.board[x][y] == Color.NONE


    def color_to_string(self, color):
        if color == Color.BLACK:
            return "BLACK"
        return "WHITE"


def play_game(game):
    root = tk.Tk()
    root.resizable(width=False, height=False)

    gui = GomokuGUI(root, game)
    game.set_gui(gui)
    gui.init_gui()

    root.mainloop()


if __name__ == "__main__":
    play_game(Gomoku())