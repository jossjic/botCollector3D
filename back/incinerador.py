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


import heapq # Librería para el método de búsquda del camino más corto A*

steps = 0

class Bot(Agent):
    w_trash=False
    def __init__(self, model, pos, incineradorAgent):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.type = "Bot"
        self.incineradorAgent = incineradorAgent
        print(self.incineradorAgent)

    def step(self):
        global steps
        
        if self.w_trash==False:
            new_pos = self.pos + np.array([self.random.randrange(-1, 2, 1),self.random.randrange(-1,2,1)])
            while (self.model.grid.out_of_bounds(new_pos) or ((new_pos[0]==((self.model.grid.width-2)//2)) and (new_pos[1]==((self.model.grid.height-2)//2)))):
                        new_pos = self.pos + np.array([self.random.randrange(-1, 2, 1),self.random.randrange(-1,2,1)])
            self.model.grid.move_agent(self, new_pos)
            if steps > 3:
                self.incineradorAgent.condition = self.incineradorAgent.OFF
                steps = 0
        else:
                new_pos = self.pos                
                if (self.pos[0] != ((self.model.grid.width-2)//2)) or (self.pos[1] != ((self.model.grid.height-2)//2)):
                    # Inicializar new_pos con la posición actual
                    
                    if self.pos[0] < ((self.model.grid.width - 2) // 2):
                        new_pos = new_pos + np.array([1, 0])
                    elif self.pos[0] > ((self.model.grid.width - 2) // 2):
                        new_pos = new_pos + np.array([-1, 0])
                    
                    if self.pos[1] < ((self.model.grid.height - 2) // 2):
                        new_pos = new_pos + np.array([0, 1])
                    elif self.pos[1] > ((self.model.grid.height - 2) // 2):
                        new_pos = new_pos + np.array([0, -1])
                            
                    elif self.pos[0] == ((self.model.grid.width-2)//2):
                        if self.pos[1] < ((self.model.grid.height-2)//2):
                            new_pos = self.pos + np.array([0,1])
                        elif self.pos[1] > ((self.model.grid.height-2)//2):
                            new_pos = self.pos + np.array([0,-1])
                    
                    elif self.pos[1] == ((self.model.grid.height-2)//2):
                        if self.pos[0] < ((self.model.grid.width-2)//2):
                            new_pos = self.pos + np.array([1,0])
                        elif self.pos[0] > ((self.model.grid.width-2)//2):
                            new_pos = self.pos + np.array([-1,0])
                    
                else:
                    self.w_trash=False
                    self.incineradorAgent.condition = self.incineradorAgent.ON
                
                if (self.incineradorAgent.condition == self.incineradorAgent.ON) and ((new_pos[0]==((self.model.grid.width-2)//2)) and (new_pos[1]==((self.model.grid.height-2)//2))):
                    self.model.grid.move_agent(self, self.pos)
                else:
                    self.model.grid.move_agent(self, new_pos)
    
                
                
        for element in self.model.grid.get_cell_list_contents([self.pos]):
            if type(element) == Basura and element.condition == element.UNCOLLECT and not self.w_trash:
                element.condition = element.COLLECT
                self.w_trash=True


class Incinerador(Agent):
    ON=1
    OFF=2
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.type = "Incinerador"
        self.condition= self.OFF
        self.timer = 0
        
    def step(self):
        # Check if the condition is ON and update the timer
        if self.condition == self.ON:
            self.timer += 1

            # Check if enough time has passed (e.g., 5 steps) and switch back to OFF
            if self.timer >= 5:
                self.condition = self.OFF
                self.timer = 0  # Reset the timer
        
class Basura(Agent):
    
    COLLECT = 0
    UNCOLLECT = 1

    def __init__(self, model):
        super().__init__(model.next_id(), model)
        self.condition = self.UNCOLLECT
        self.type = "Basura"
        

class   Sala(Model):
    def getGridSize(self):
        return self.grid.width, self.grid.height
    
    def __init__(self, density=0.45, grid_size=False, max_steps=1000, conta = 0):
        super().__init__()
        
        if grid_size:
            self.grid = MultiGrid(51, 51, torus=False)
        else:
            self.grid = MultiGrid(21, 21, torus=False)
        self.schedule = RandomActivation(self)
        self.max_steps = max_steps
       
        
        print(self.grid.width, self.grid.height)

        incinerador = Incinerador(self, ((self.grid.width-2)//2, (self.grid.height-2)//2))  
        self.grid.place_agent(incinerador, incinerador.pos)
        self.schedule.add(incinerador)
        
        robot1 = Bot(self, (0, 0), incinerador)
        self.grid.place_agent(robot1, robot1.pos)
        self.schedule.add(robot1)
                

        robot2 = Bot(self, (0, self.grid.height - 1), incinerador)  
        self.grid.place_agent(robot2, robot2.pos)
        self.schedule.add(robot2)
                

        robot3 = Bot(self, (self.grid.width-1, 0), incinerador)  
        self.grid.place_agent(robot3, robot3.pos)
        self.schedule.add(robot3)
                

        robot4 = Bot(self, (self.grid.width-1, self.grid.height-1), incinerador)  
        self.grid.place_agent(robot4, robot4.pos)
        self.schedule.add(robot4)
                
            
        robot5 = Bot(self, ((self.grid.width-1)//2, (self.grid.height-1)//2), incinerador)  
        self.grid.place_agent(robot5, robot5.pos)
        self.schedule.add(robot5)


        for _,(x,y) in self.grid.coord_iter():  
            if self.random.random() < density:
                basura = Basura(self)
                self.grid.place_agent(basura, (x,y))
                self.schedule.add(basura)

        self.datacollector = DataCollector({"Percent burned": lambda m: self.count_type(m, Basura.COLLECT) / len(self.schedule.agents)})
                        
             
    def count_type(model, condition):
        count = 0
        for Basura in model.schedule.agents:
            if Basura.condition == condition:
                count += 1
                print(count)
        return count       

    def step(self):
        global steps
        if self.schedule.time < self.max_steps:
            self.schedule.step()
            steps += 1
            print(steps)
            

