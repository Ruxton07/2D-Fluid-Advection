import tkinter as tk
from tkinter import messagebox

class GridMakerSubprocess:
    def __init__(self, n, m):
        self.n = n
        self.m = m
        self.grid = [[0 for _ in range(m)] for _ in range(n)]
        self.window = tk.Tk()
        self.window.title("Grid Maker Subprocess")
        self.buttons = [[None for _ in range(m)] for _ in range(n)]
        self.white_image = tk.PhotoImage(width=10, height=10)
        self.black_image = tk.PhotoImage(width=10, height=10)
        self.black_image.put(("black",), to=(0, 0, 10, 10))
        self.first_click = None
        self.create_grid()
        self.create_submit_button()
        self.window.mainloop()

    def create_grid(self):
        for i in range(self.n):
            for j in range(self.m):
                button = tk.Button(self.window, image=self.white_image, padx=0, pady=0)
                button.grid(row=i, column=j, padx=1, pady=1)
                button.bind("<Button-1>", lambda event, i=i, j=j: self.on_button_click(event, i, j))
                self.buttons[i][j] = button

    def toggle_button(self, i, j, toggle_range=False):
        if toggle_range:
            if self.grid[i][j] == 0:
                self.grid[i][j] = 1
                self.buttons[i][j].config(image=self.black_image)
            else:
                self.grid[i][j] = 0
                self.buttons[i][j].config(image=self.white_image)
        else:
            if self.grid[i][j] == 0:
                self.grid[i][j] = 1
                self.buttons[i][j].config(image=self.black_image)
            else:
                self.grid[i][j] = 0
                self.buttons[i][j].config(image=self.white_image)

    def create_submit_button(self):
        submit_button = tk.Button(self.window, text="Submit", command=self.submit)
        submit_button.grid(row=self.n, columnspan=self.m, pady=5)

    def submit(self):
        formatted_grid = "[" + ",\n ".join(str(row) for row in self.grid) + "]"
        print("Generated Grid:")
        print(formatted_grid)
        messagebox.showinfo("Grid", f"Generated Grid:\n{formatted_grid}")
        self.window.destroy()

    def on_button_click(self, event, i, j):
        if event.state & 0x0001:  # Check if Shift key is pressed
            if self.first_click is None:
                self.first_click = (i, j)
            else:
                self.toggle_range(self.first_click, (i, j))
                self.first_click = None
        else:
            self.toggle_button(i, j)

    def toggle_range(self, start, end):
        start_i, start_j = start
        end_i, end_j = end
        for i in range(min(start_i, end_i), max(start_i, end_i) + 1):
            for j in range(min(start_j, end_j), max(start_j, end_j) + 1):
                self.toggle_button(i, j, toggle_range=True)

# Example usage
if __name__ == "__main__":
    GridMakerSubprocess(40, 40)