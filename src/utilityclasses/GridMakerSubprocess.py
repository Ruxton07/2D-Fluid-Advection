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
        self.create_grid()
        self.create_submit_button()
        self.window.mainloop()

    def create_grid(self):
        for i in range(self.n):
            for j in range(self.m):
                button = tk.Button(self.window, image=self.white_image, command=lambda i=i, j=j: self.toggle_button(i, j), padx=0, pady=0)
                button.grid(row=i, column=j, padx=1, pady=1)
                self.buttons[i][j] = button

    def toggle_button(self, i, j):
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

# Example usage
if __name__ == "__main__":
    GridMakerSubprocess(40, 40)