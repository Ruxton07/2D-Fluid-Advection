class GridObject:
    def __init__(self, density=-1, index=(0,0), is_land=False):
        self.Density = density
        self.index = index
        self.IsLand = is_land
    
    def __str__(self):
        return str(self.Density) + " "