from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Checkbox
from mesa.visualization.UserParam import Slider
from mesa.visualization.modules import ChartModule
from mesa.datacollection import DataCollector
import numpy as np
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class Agentes(Agent):
    with_trash="With trash"
    without_trash="Without trash"
    def __init__(self, model, pos, incineradorAgent):
        super().__init__(model.next_id(), model)
        self.condition = self.without_trash
        self.pos = pos
        self.type = "robot"
        self.incineradorAgent = incineradorAgent

    def step(self):
        global globalMatrix
        if not self.condition == self.with_trash:
            possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]  
            
            new_pos = self.pos + np.array(self.random.choice(possible_moves))
            
            while (self.model.grid.out_of_bounds(new_pos) or (new_pos[0] == self.incineradorAgent.pos[0] and new_pos[1] == self.incineradorAgent.pos[1])):
                new_pos = self.pos + np.array(self.random.choice(possible_moves))
            
            self.model.grid.move_agent(self, new_pos)
            

        else:     
            new_pos = self.pos    
            if (self.pos[0] != self.incineradorAgent.pos[0]) or (self.pos[1] != self.incineradorAgent.pos[1]):
                grid = Grid(matrix=globalMatrix.tolist())
                finder = AStarFinder()
                (r1, r2) = self.incineradorAgent.pos 
                (g1, g2) = self.pos
                incinerador_pos = grid.node(r1, r2)
                self_pos = grid.node(g1, g2)
                path, _ = finder.find_path(self_pos, incinerador_pos, grid)
                if len(path) > 1:
                    new_pos = (path[1].x, path[1].y)

                        
            else:
                self.condition = self.without_trash
                self.incineradorAgent.condition = self.incineradorAgent.ON
            incineradorOn = self.incineradorAgent.condition == self.incineradorAgent.ON and new_pos[0]==self.incineradorAgent.pos[0] and new_pos[1]==self.incineradorAgent.pos[1]
            if not incineradorOn:
                self.model.grid.move_agent(self, new_pos)
    
                
                
        for element in self.model.grid.get_cell_list_contents([self.pos]):
            if type(element) == Basura and element.condition == element.UNCOLLECT and not self.condition == self.with_trash:
                element.condition = element.COLLECT
                globalMatrix[self.pos[1]][self.pos[0]]=1
                self.condition = self.with_trash


class Incinerador(Agent):
    ON="ON"
    OFF="OFF"
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.type = "incinerador"
        self.condition= self.OFF
        self.timer = 0
        
    def step(self):
        if self.condition == self.ON:
            self.timer += 1

            if self.timer >= 5:
                self.condition = self.OFF
                self.timer = 0 
        
class Basura(Agent):
    
    COLLECT = "COLLECT"
    UNCOLLECT = "UNCOLLECT"

    def __init__(self, model):
        super().__init__(model.next_id(), model)
        self.condition = self.UNCOLLECT
        self.type = "basura"
        

class   Sala(Model):
    
    def getGridSize(self):
        return self.grid.width, self.grid.height
    
    def __init__(self, density=0.4, grid_size=False, conta = 0):
        super().__init__()
        global globalMatrix
        
        if grid_size:
            self.grid = MultiGrid(51, 51, torus=False)
        else:
            self.grid = MultiGrid(21, 21, torus=False)
        self.schedule = RandomActivation(self)
        self.matrix = np.ones((self.grid.width, self.grid.height), dtype=np.int8)
        incinerador = Incinerador(self, ((self.grid.width-2)//2, (self.grid.height-2)//2))  
        self.grid.place_agent(incinerador, incinerador.pos)
        self.schedule.add(incinerador)
        
        for _,(x,y) in self.grid.coord_iter():  
            if self.random.random() < density and (x,y)!=(incinerador.pos[0],incinerador.pos[1]) and (x,y)!=(0,0) and (x,y)!=(0,self.grid.height-1) and (x,y)!=(self.grid.width-1,0) and (x,y)!=(self.grid.width-1,self.grid.height-1):
                basura = Basura(self)
                self.grid.place_agent(basura, (x,y))
                self.schedule.add(basura)
                self.matrix[y][x]=0
                
        globalMatrix = self.matrix
        
        
        robot1 = Agentes(self, (0, 0), incinerador)
        self.grid.place_agent(robot1, robot1.pos)
        self.schedule.add(robot1)
                

        robot2 = Agentes(self, (0, self.grid.height - 1), incinerador)  
        self.grid.place_agent(robot2, robot2.pos)
        self.schedule.add(robot2)
                

        robot3 = Agentes(self, (self.grid.width-1, 0), incinerador)  
        self.grid.place_agent(robot3, robot3.pos)
        self.schedule.add(robot3)
                

        robot4 = Agentes(self, (self.grid.width-1, self.grid.height-1), incinerador)  
        self.grid.place_agent(robot4, robot4.pos)
        self.schedule.add(robot4)
                
            
        robot5 = Agentes(self, ((self.grid.width-1)//2, (self.grid.height-1)//2), incinerador)  
        self.grid.place_agent(robot5, robot5.pos)
        self.schedule.add(robot5)
        
    def step(self):
        self.schedule.step()
