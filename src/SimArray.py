import GridObject

class SimArray:
    # default value is 40x40 array of 0s
    def __init__(self, array=[[0 for x in range(40)] for y in range(40)]):
        self.grid = [[0 for x in range(40)] for y in range(40)]
        for x in range(len(array)):
            for y in range(len(array[0])):
                self.grid[x][y] = GridObject.GridObject(array[x][y], (x, y))
                
    
    def len(self):
        return len(self.grid)
    
    def __getitem__(self, key):
        return self.grid[key]
    
    def __str__(self):
        #return string representation of self.grid where each GridObject.GridObject is called with print()
        return '\n' + '\n'.join([''.join([str(cell) for cell in row]) for row in self.grid])
    
    def printIndices(self):
        #return string representation of self.grid where each GridObject.GridObject is called with print()
        return '\n' + '\n'.join([''.join([str(cell.index) for cell in row]) for row in self.grid])
    
    def copy(self):
        #print(self)
        #print(SimArray([[self.grid[x][y].Density for y in range(len(self.grid[0]))] for x in range(len(self.grid))]))
        return SimArray([[self.grid[x][y].Density for y in range(len(self.grid[0]))] for x in range(len(self.grid))])
    
    