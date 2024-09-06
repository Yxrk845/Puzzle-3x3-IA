import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from PIL import Image, ImageTk
from heapq import heappop, heappush

# Configuración del tablero inicial (puedes cambiarlo)
PUZZLE_SIZE = 3
goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]  # Estado final deseado

class Puzzle:
    def __init__(self, initial_state, image_path):
        self.initial_state = initial_state
        self.window = tk.Tk()
        self.window.title("Puzzle 3x3 con Imagen Dividida")
        self.buttons = []
        self.images = {}
        self.image_path = image_path
        self.load_and_split_image()
        self.create_ui()
        self.window.mainloop()

    def load_and_split_image(self):
        # Cargar la imagen completa
        image = Image.open(self.image_path)
        image = image.resize((300, 300), Image.ANTIALIAS)  # Ajusta el tamaño de la imagen a 300x300
        width, height = image.size
        piece_width = width // PUZZLE_SIZE
        piece_height = height // PUZZLE_SIZE
        
        # Dividir la imagen en 9 partes (8 piezas y 1 espacio vacío)
        for i in range(PUZZLE_SIZE):
            for j in range(PUZZLE_SIZE):
                if i * PUZZLE_SIZE + j < PUZZLE_SIZE * PUZZLE_SIZE - 1:
                    box = (j * piece_width, i * piece_height, (j + 1) * piece_width, (i + 1) * piece_height)
                    piece = image.crop(box)
                    self.images[i * PUZZLE_SIZE + j + 1] = ImageTk.PhotoImage(piece)

        # Añadir imagen en blanco para el espacio vacío
        blank_image = Image.new("RGB", (piece_width, piece_height), (255, 255, 255))
        self.images[0] = ImageTk.PhotoImage(blank_image)

    def create_ui(self):
        for i in range(PUZZLE_SIZE):
            row = []
            for j in range(PUZZLE_SIZE):
                button = tk.Button(self.window, image=self.images[self.initial_state[i][j]], width=100, height=100)
                button.grid(row=i, column=j)
                row.append(button)
            self.buttons.append(row)

        # Botón para resolver el puzzle
        solve_button = tk.Button(self.window, text="Resolver", command=self.solve_puzzle)
        solve_button.grid(row=PUZZLE_SIZE, columnspan=PUZZLE_SIZE)

        # Área de texto para mostrar la ruta
        self.route_display = scrolledtext.ScrolledText(self.window, width=40, height=10)
        self.route_display.grid(row=PUZZLE_SIZE + 1, columnspan=PUZZLE_SIZE)

        # Área de texto para mostrar el State Space (estados explorados)
        self.state_space_display = scrolledtext.ScrolledText(self.window, width=40, height=10)
        self.state_space_display.grid(row=0, column=PUZZLE_SIZE + 1, rowspan=PUZZLE_SIZE)

    def solve_puzzle(self):
        result = self.a_star(self.initial_state)
        if result:
            self.route_display.insert(tk.END, "Solución encontrada:\n")
            for step in result:
                self.route_display.insert(tk.END, f"{step}\n")
            self.animate_solution(result)
        else:
            messagebox.showinfo("Error", "No se encontró solución")

    def find_blank(self, state):
        for i in range(PUZZLE_SIZE):
            for j in range(PUZZLE_SIZE):
                if state[i][j] == 0:
                    return i, j

    def generate_neighbors(self, state):
        x, y = self.find_blank(state)
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < PUZZLE_SIZE and 0 <= new_y < PUZZLE_SIZE:
                new_state = [row[:] for row in state]
                new_state[x][y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[x][y]
                neighbors.append(new_state)
        return neighbors

    def heuristic(self, state):
        # Distancia de Manhattan
        distance = 0
        for i in range(PUZZLE_SIZE):
            for j in range(PUZZLE_SIZE):
                value = state[i][j]
                if value != 0:
                    target_x = (value - 1) // PUZZLE_SIZE
                    target_y = (value - 1) % PUZZLE_SIZE
                    distance += abs(target_x - i) + abs(target_y - j)
        return distance

    def a_star(self, initial):
        heap = []
        heappush(heap, (0, initial, []))
        visited = set()
        while heap:
            cost, state, path = heappop(heap)
            if state == goal_state:
                return path + [state]
            visited.add(str(state))
            self.state_space_display.insert(tk.END, f"Explorado: {state}\n")  # Mostrar estado explorado
            for neighbor in self.generate_neighbors(state):
                if str(neighbor) not in visited:
                    new_cost = cost + 1 + self.heuristic(neighbor)
                    heappush(heap, (new_cost, neighbor, path + [state]))
        return None

    def animate_solution(self, solution):
        def update_buttons(state):
            for i in range(PUZZLE_SIZE):
                for j in range(PUZZLE_SIZE):
                    self.buttons[i][j]['image'] = self.images[state[i][j]]

        for step in solution:
            self.window.after(500, update_buttons(step))
            self.window.update()
            self.window.after(500)

if __name__ == "__main__":
    initial_state = [[1, 0, 2], [7, 8, 3], [4, 5, 6]] 
    image_path = "Pythonlog.jpg"  
    Puzzle(initial_state, image_path)
        