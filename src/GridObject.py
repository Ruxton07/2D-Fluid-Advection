class GridObject:
    def __init__(self, density: float = -1.0, index: tuple = (0, 0), is_land: bool = False):
        self.Density = density
        self.index = index
        self.IsLand = is_land
        self.ux = 0.0  # Velocity in the x direction
        self.uy = 0.0  # Velocity in the y direction
    
    def __str__(self):
        return str(self.Density) + " "