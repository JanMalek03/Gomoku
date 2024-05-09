import tkinter as tk
from tkinter import ttk
from enum import Enum
import time
import random

BOARD_SIZE = 15
SWAP2 = True


class Color(Enum):
    NONE = 0
    BLACK = 1
    WHITE = 2


class GomokuGUI:
    def __init__(self, master, game, size=15):
        self.game = game
        self.master = master
        self.master.title("Gomoku")

        self.canvas = tk.Canvas(self.master, width=size*30, height=size*30, bg="#BF8962")
        if not SWAP2:
            self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.pack()

        self.size = size
        self.circle_radius = 12

        self.draw_board()

        self.text_visible = False
        self.reset_button = ttk.Button(self.master, text="Reset Game", command=lambda: self.reset_game())
        if SWAP2:
            self.button_frame = tk.Frame(self.master)
            self.button_frame.pack(fill=tk.X, pady=0)


    def init_gui(self):
        self.canvas.delete("all")
        self.reset_button.pack_forget()
        self.draw_board()

        self.reset_button.pack()

        if SWAP2:
            self.swap_extra()


    def swap_extra(self):
        self.black_button = ttk.Button(self.button_frame, text="Play as BLACK", command=lambda: self.choose_color(Color.BLACK))
        self.black_button.pack(side=tk.LEFT, padx=10, expand=True)

        self.place_stones_button = ttk.Button(self.button_frame, text="Place BLACK and WHITE", command=self.enable_initial_stone_placement)
        self.place_stones_button.pack(side=tk.LEFT, padx=10, expand=True)

        self.white_button = ttk.Button(self.button_frame, text="Play as WHITE", command=lambda: self.choose_color(Color.WHITE))
        self.white_button.pack(side=tk.LEFT, padx=10, expand=True)

        self.current_stone_label = tk.Label(self.button_frame, text="")

        self.place_initial_moves()


    def enable_initial_stone_placement(self):
        self.black_button.pack_forget()
        self.white_button.pack_forget()
        self.place_stones_button.pack_forget()

        self.current_stone_label.pack(side=tk.TOP, padx=10)
        self.current_stone_label.config(text="Place BLACK stone")
        self.text_visible = True

        self.canvas.bind("<Button-1>", self.on_initial_stone_click)
        self.initial_stones_placed = 0


    def on_initial_stone_click(self, event):
        x, y = event.x, event.y
        board_x = x // 30
        board_y = y // 30
        if ((board_x) >= BOARD_SIZE or (board_y) >= BOARD_SIZE) or self.initial_stones_placed >= 2:
            return
        if not self.game.is_valid(board_x, board_y):
            return
        if self.initial_stones_placed == 0:
            self.game.make_move(board_x, board_y, Color.BLACK, initial=True)
            self.current_stone_label.config(text="Place WHITE stone")
        elif self.initial_stones_placed == 1:
            self.game.make_move(board_x, board_y, Color.WHITE, initial=True)
        self.initial_stones_placed += 1

        if self.initial_stones_placed == 2:
            self.canvas.unbind("<Button-1>")

            best_color = None
            black_value = self.game.evaluate_starting(Color.BLACK)
            white_value = self.game.evaluate_starting(Color.WHITE)
            if black_value >= white_value:
                best_color = Color.BLACK
            else:
                best_color = Color.WHITE

            self.game.player_color = self.game.get_opposite_color(best_color)
            self.current_stone_label.config(text=f"You are playing as {self.game.color_to_string(self.game.player_color)}")

            if best_color == Color.WHITE:
                self.game.ai_make_move()

            self.canvas.bind("<Button-1>", self.on_canvas_click)


    def choose_color(self, color):
        self.place_stones_button.pack_forget()

        self.game.player_color = color
        if color == Color.BLACK:
             self.game.ai_make_move()

        self.black_button.pack_forget()
        self.white_button.pack_forget()

        self.canvas.bind("<Button-1>", self.on_canvas_click)


    def place_initial_moves(self):
        openings = [
            [(7, 7, Color.BLACK), (7, 8, Color.BLACK), (8, 7, Color.WHITE)],
            [(7, 7, Color.BLACK), (8, 8, Color.BLACK), (6, 6, Color.WHITE)],
            [(7, 7, Color.BLACK), (7, 8, Color.BLACK), (7, 6, Color.WHITE)],
            [(7, 7, Color.BLACK), (8, 7, Color.BLACK), (6, 7, Color.WHITE)],
            [(7, 7, Color.BLACK), (8, 7, Color.BLACK), (7, 8, Color.WHITE)],
            [(5, 6, Color.BLACK), (8, 9, Color.BLACK), (7, 7, Color.WHITE)],
            [(6, 6, Color.BLACK), (8, 7, Color.BLACK), (8, 6, Color.WHITE)],
            [(6, 7, Color.BLACK), (9, 7, Color.BLACK), (7, 7, Color.WHITE)]
        ]
        chosen_opening = random.choice(openings)
        for x, y, color in chosen_opening:
            self.game.make_move(x, y, color, initial=True)


    def game_over(self):
        self.canvas.unbind("<Button-1>")


    def draw_board(self):
        for i in range(self.size):
            for j in range(self.size):
                x1, y1 = i * 30, j * 30
                x2, y2 = x1 + 30, y1 + 30
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", tags=(i, j))


    def on_canvas_click(self, event):
        if self.text_visible:
            self.current_stone_label.pack_forget()

        x, y = event.x, event.y
        start_time = time.time()
        board_x = x // 30
        board_y = y // 30
        if ((board_x) >= BOARD_SIZE or (board_y) >= BOARD_SIZE):
            return
        ended = self.game.make_move(board_x, board_y, self.game.player_color)
        if not ended:
            self.master.after(1, lambda: self.finish_ai_move(start_time))


    def finish_ai_move(self, start_time):
        self.game.ai_make_move()
        end_time = time.time()
        duration_ms = round((end_time - start_time) * 1000, 2)
        print("AI move time:", duration_ms, "ms")


    def place_circle(self, i, j, color, outline_color="black", outline_width=1):
        x, y = i * 30 + 15, j * 30 + 15
        circle_id = self.canvas.create_oval(x - self.circle_radius, y - self.circle_radius,
                                            x + self.circle_radius, y + self.circle_radius,
                                            outline=outline_color, fill=color, width=outline_width)
        return circle_id


    def place_dot(self, x, y):
        center_x = x * 30 + 15
        center_y = y * 30 + 15
        dot_radius = 3

        self.canvas.create_oval(
            center_x - dot_radius, center_y - dot_radius,
            center_x + dot_radius, center_y + dot_radius,
            fill="red", outline="red", width=2
        )


    def highlight_winning_cells(self, winning_cells):
        for i, j in winning_cells:
            self.place_circle(i, j, "white" if self.game.board[i][j] == Color.WHITE else "black", "red", 3)


    def reset_board(self):
        self.canvas.delete("all")
        self.draw_board()


    def reset_game(self):
        self.game.initialize_game()
        self.canvas.delete("all")

        self.reset_button.pack_forget()

        if SWAP2:
            self.white_button.pack_forget()
            self.black_button.pack_forget()
            self.place_stones_button.pack_forget()
            self.current_stone_label.pack_forget()

        self.draw_board()
        if SWAP2:
            self.canvas.unbind("<Button-1>")
        else:
            self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.reset_button = ttk.Button(self.master, text="Reset Game", command=lambda: self.reset_game())
        self.reset_button.pack()

        if SWAP2:
            self.swap_extra()
