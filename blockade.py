"""
Common definitions for the Blockade players.


This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

"""

import random
import itertools
import operator
import math
from queue import PriorityQueue
import heapq

PLAYER1 = 0
PLAYER2 = 1


class InvalidAction(Exception):
    """Raised when an invalid action is played."""

    def __init__(self, action=None, player=-1):
        self.action = action
        self.player = player


class NoPath(Exception):
    """Raised when a player puts a guard such that no path exists
    between a player and its goal row"""

    def __repr__(self):
        return "Exception: no path to reach the goal"

'''is_gm=False
guard_location=(-1,-1)'''
class Board:
    """
    Representation of a Blockade Board.

    """
    def __init__(self, percepts=None):
        """
        Constructor of the representation for a blockade game of size 12.
        The representation can be initialized by a percepts
        If percepts==None:
            player 0 is position (8,2) and its goal is to reach the raw 11
            player 1 is position (5,11) and its goal is to reach the raw 0
            each player owns 6 guards and there is initially no guard on the
            board
        """
        self.size = 12
        self.rows = self.size
        self.cols = self.size
        self.starting_guards = 6
        self.kings = [(1, 7), (10, 4)]
        self.goals = [11, 0]
        self.nb_guards = [self.starting_guards, self.starting_guards]
        self.guards = []
        self.movable_guards=[[],[]]
        if percepts is not None:
            self.kings[0] = (percepts["kings"][0][0],percepts["kings"][0][1])
            self.goals[0] = percepts["goals"][0]
            self.kings[1] = (percepts["kings"][1][0],percepts["kings"][1][1])
            self.goals[1] = percepts["goals"][1]
            for (x, y) in percepts["guards"]:
                self.guards.append((x, y))
            self.nb_guards[0] = percepts["nb_guards"][0]
            self.nb_guards[1] = percepts["nb_guards"][1]
    def pretty_print(self):
        """print of the representation"""
        print("Player 0 => king:", self.kings[0], "goal:",
              self.goals[0], "nb guards:", self.nb_guards[0])
        print("Player 1 => king:", self.kings[1], "goal:",
              self.goals[1], "nb guards:", self.nb_guards[1])
        print("Guards:", self.guards)

    def __str__(self):
        """String representation of the board"""
        board_str = ""
        for i in range(self.size):
            for j in range(self.size):
                if self.kings[0][0] == i and self.kings[0][1] == j:
                    board_str += " P1"
                elif self.kings[1][0] == i and self.kings[1][1] == j:
                    board_str += " P2"
                elif (i, j) in self.guards:
                    board_str += " X "
                else:
                    board_str += " 0 "
            board_str += "\n"

        return board_str

    def clone(self):
        """Return a clone of this object."""
        clone_board = Board()
        clone_board.kings[0] = self.kings[0]
        clone_board.kings[1] = self.kings[1]
        clone_board.goals[0] = self.goals[0]
        clone_board.goals[1] = self.goals[1]
        clone_board.nb_guards[0] = self.nb_guards[0]
        clone_board.nb_guards[1] = self.nb_guards[1]
        for (x, y) in self.movable_guards[0]:
            clone_board.movable_guards[0].append((x, y))
        for (x, y) in self.movable_guards[1]:
            clone_board.movable_guards[1].append((x, y))
        for (x, y) in self.guards:
            clone_board.guards.append((x, y))

        return clone_board

    def play_action(self, action, player):
        """Play an action if it is valid.

        If the action is invalid, raise an InvalidAction exception.
        Return self.

        Arguments:
        action -- the action to be played
        player -- the player who is playing

        """
        
        try:
            '''global is_gm
            global guard_location
            if is_gm:
                action = (action[0],guard_location[0],guard_location[1],action[1],action[2])
                is_gm=False
                guard_location=(-1,-1)'''
            if len(action) != 3: #G,GM,K
                if len(action) != 5: #GM with previous guard position info
                    raise InvalidAction(action, player)
                else:

                    name = action[0]
                    guard_loc = (action[1],action[2])
                    loc = (action[3],action[4])
                    if name =='GM':
                        if self.nb_guards[player]!=0: # still have remaining guards to place
                            raise InvalidAction(action, player)
                        elif not (guard_loc[0]==loc[0] or guard_loc[1]==loc[1]):
                            raise InvalidAction(action, player)
                        elif not (guard_loc in self.movable_guards[player]):
                            raise InvalidAction(action, player)
                        elif not (0<= loc[0]< self.size and 0<=loc[1]< self.size): # in the board
                            raise InvalidAction(action, player)
                        elif loc in self.guards: # guard on top of the existing guard
                            raise InvalidAction(action, player)
                        elif loc[0] in [self.kings[0][0]-1,self.kings[0][0],self.kings[0][0]+1]  and loc[1] in [self.kings[0][1]-1,self.kings[0][1],self.kings[0][1]+1]: # no guard at p1 king's field
                            raise InvalidAction(action, player)
                        elif loc[0] in [self.kings[1][0]-1,self.kings[1][0],self.kings[1][0]+1]  and loc[1] in [self.kings[1][1]-1,self.kings[1][1],self.kings[1][1]+1]: # no guard at p2 king's field
                            raise InvalidAction(action, player)
                        
                        obsticles =[]
                        obsticles.extend(self.guards)
                        obsticles.extend(self.kings)
                        if guard_loc[0]==loc[0]:
                            if guard_loc[1]<loc[1]:
                                for i in range(guard_loc[1]+1,loc[1]):
                                    if (guard_loc[0],i) in obsticles:
                                        raise InvalidAction(action, player)
                            else:
                                for i in range(loc[1]+1,guard_loc[1]):
                                    if (guard_loc[0],i) in obsticles:
                                        raise InvalidAction(action, player)
                        else:
                            if guard_loc[0]<loc[0]:
                                for i in range(guard_loc[0]+1,loc[0]):
                                    if (i,guard_loc[1]) in obsticles:
                                        raise InvalidAction(action, player)
                            else:
                                for i in range(loc[0]+1,guard_loc[0]):
                                    if (i,guard_loc[1]) in obsticles:
                                        raise InvalidAction(action, player)
                        self.movable_guards[player].remove(guard_loc)
                        self.guards.remove(guard_loc)
                        self.movable_guards[player].append(loc)
                        self.guards.append(loc)
                    else:
                        raise InvalidAction(action, player)
            else:
                name = action[0]
                loc = (action[1],action[2])
                
                if name =='G':
                    if self.nb_guards[player]==0: # no guards left
                        raise InvalidAction(action, player)
                    elif not (0<= loc[0]< self.size and 0<=loc[1]< self.size): # in the board
                        raise InvalidAction(action, player)
                    elif self.nb_guards[player]==6 and loc[0]%3==1 and loc[1]%3==1: #no first guard at the center
                        raise InvalidAction(action, player)
                    elif loc[0] in [self.kings[0][0]-1,self.kings[0][0],self.kings[0][0]+1]  and loc[1] in [self.kings[0][1]-1,self.kings[0][1],self.kings[0][1]+1]: # no guard at p1 king's field
                        raise InvalidAction(action, player)
                    elif loc[0] in [self.kings[1][0]-1,self.kings[1][0],self.kings[1][0]+1]  and loc[1] in [self.kings[1][1]-1,self.kings[1][1],self.kings[1][1]+1]: # no guard at p2 king's field
                        raise InvalidAction(action, player)
                    elif loc in self.guards: # guard on top of the existing guard
                        raise InvalidAction(action, player)
                    self.movable_guards[player].append(loc)
                    self.guards.append(loc)
                    self.nb_guards[player]=self.nb_guards[player]-1
                elif name =='GM':
                    if self.nb_guards[player]!=0: # still have remaining guards to place
                        raise InvalidAction(action, player)
                    elif not (0<= loc[0]< self.size and 0<=loc[1]< self.size): # in the board
                        raise InvalidAction(action, player)
                    elif loc in self.guards: # guard on top of the existing guard
                        raise InvalidAction(action, player)
                    elif loc[0] in [self.kings[0][0]-1,self.kings[0][0],self.kings[0][0]+1]  and loc[1] in [self.kings[0][1]-1,self.kings[0][1],self.kings[0][1]+1]: # no guard at p1 king's field
                        raise InvalidAction(action, player)
                    elif loc[0] in [self.kings[1][0]-1,self.kings[1][0],self.kings[1][0]+1]  and loc[1] in [self.kings[1][1]-1,self.kings[1][1],self.kings[1][1]+1]: # no guard at p2 king's field
                        raise InvalidAction(action, player)
                    
                    leg = [None,None,None,None]
                    def fill(axis,item,typ):
                        inv = (axis+1)%2 # other axis
                        leg1 = axis*2 # left side or up
                        leg2 = axis*2+1 #r ight side or bottom
                        dist = abs(item[inv]-loc[inv]) # distance between the item and GM position
                        if item[inv]<loc[inv]: # if the item is on the left/bottom of the GM position
                                if leg[leg1]== None or leg[leg1][2]>dist: # if this item is closer than the previous ones
                                    leg[leg1]=[item,typ,dist] # assign this item to leg[0] (left) or leg[2] (bottom)
                        else: # if the item is on the right/up of the GM position
                                if leg[leg2] == None or leg[leg2][2]>dist: # if this item is closer than the previous ones
                                    leg[leg2]=[item,typ,dist] # assign this item to leg[1] (right) or leg[3] (up)
                
                    for sel in self.movable_guards[player]: # in the player's guards
                        if sel[0]==loc[0]: # if at the same row
                            fill(0,sel,"m") # assign to the leg[0] or leg[1]
                        elif sel[1]==loc[1]: # if at the same column
                            fill(1,sel,"m") # assign to the leg[2] or leg[3]
                    for sel in self.movable_guards[(player+1)%2]: # other player
                        if sel[0]==loc[0]: # if at the same row
                            fill(0,sel,"o") # assign to the leg[0] or leg[1]
                        elif sel[1]==loc[1]: # if at the same column
                            fill(1,sel,"o") # assign to the leg[2] or leg[3]
                    for sel in self.kings: # if a king
                        if sel[0]==loc[0]: # if at the same row
                            fill(0,sel,"k") # assign to the leg[0] or leg[1]
                        elif sel[1]==loc[1]: # if at the same column
                            fill(1,sel,"k") # assign to the leg[2] or leg[3]
                    min_val = self.size #=12 in order to find the min distance object ("m")
                    chosen = (-1,-1)
                    for candidate in leg: # for the objects at the all 4 dimentions
                        if candidate!=None and candidate[1]=="m" and min_val > candidate[2]:
                            min_val=candidate[2]
                            chosen=candidate[0]
                    if chosen ==  (-1,-1): # there is not a valid object ("m") to move
                        raise InvalidAction(action, player)
                    else:
                        self.movable_guards[player].remove(chosen)
                        self.guards.remove(chosen)
                        self.movable_guards[player].append(loc)
                        self.guards.append(loc)
                elif name =='K':
                    # if self.nb_guards[player]!=0: #all the guards placed
                        # raise InvalidAction(action, player)
                    # elif not (0<= loc[0]< self.size and 0<=loc[1]< self.size): #not in the board
                    if len(self.guards)==0: # if it is the first move
                        raise InvalidAction(action, player)
                    if not (0<=loc[1]< self.size): # not in the board
                        raise InvalidAction(action, player)
                    elif not loc[0]==self.goals[player]: # not equal to 0 or 11
                        raise InvalidAction(action, player)
                    elif loc in self.guards: # if there is a guard on the K's goal position
                        raise InvalidAction(action, player)
                    else:
                        self.add_vertices(0,self.size,player) # min_lim=0, max_lim=12
                        self.dijkstra(self.v[str(self.kings[player][0])+","+str(self.kings[player][1])])
                        if self.hasPathTo(self.v[str(loc[0])+","+str(loc[1])]):
                            self.kings[player]=loc
                        else:
                            raise InvalidAction(action, player)

                else: # not equal to G,GM or K
                    raise InvalidAction(action, player)
                #print(self.actions((player+1)%2))
            return self
        except Exception:
            print(format(Exception))
            raise InvalidAction(action, player)
    
    def actions(self,player):
        if not self.is_finished(): # if any of the kings are not at their goal rows
            if len(self.guards)!=0: # if there is at least one guard placed on the board
                self.add_vertices(0,self.size,player) #min_lim=0, max_lim=12
                self.dijkstra(self.v[str(self.kings[player][0])+","+str(self.kings[player][1])]) # dijkstra is called with the start vertex: king of the player
                loc = self.min_path(player) # loc = a point at the goal row with min dist where escape is possible (no guard)
                if loc[0]!=-1 and loc[1]!=-1: # if there is a possible escape on the goal row
                    return [("K",loc[0],loc[1])] # K,x:0 or 11,y
            if self.nb_guards[player]==6: #if there is no guard placed by player
                # x in range of the board limits, is not in center, not in other king's field, not on top of a guard already placed at the board, and ( must be smaller than 10 for P1, or must be greater than 1 for P2 )
                # G,x,y:4 or 7
                return [("G",x, self.kings[(player+1)%2][1]) for x in range(self.size)  if not (x%3==1) and not(x in [self.kings[(player+1)%2][0]-1,self.kings[(player+1)%2][0],self.kings[(player+1)%2][0]+1]) and not((x,self.kings[(player+1)%2][1]) in self.guards) and ((player == 0 and x<self.kings[(player+1)%2][0]) or (player == 1 and x>self.kings[(player+1)%2][0]))]
            elif self.nb_guards[player] !=0: #if all the guards are not placed (still guards on hand) 'G' action is valid
                # x,y in range of board limits, x,y is not in the field og kings, and not on top of a guard already placed at the board
                # G,x,y (allowed)
                return [("G",x, y) for x in range(self.size) for y in range(self.size) if not(x in [self.kings[0][0]-1,self.kings[0][0],self.kings[0][0]+1]  and y in [self.kings[0][1]-1,self.kings[0][1],self.kings[0][1]+1]) and not(x in [self.kings[1][0]-1,self.kings[1][0],self.kings[1][0]+1]  and y in [self.kings[1][1]-1,self.kings[1][1],self.kings[1][1]+1]) and not((x,y) in self.guards)]
            elif self.nb_guards[player] ==0: # if all the guards of player are placed (no more 'G' actions allowed)
                obsticles=[]
                obsticles.extend(self.guards) # all the guards on the board are added to the obstacles
                obsticles.extend(self.kings) # kings are added to the obstacles
                increment = [True,True,True,True]
                move = [] # possible moves to be returned (GM)
                for guard in self.movable_guards[player]: # for each guards of the player on the board
                    increment[0]=True
                    increment[1]=True
                    increment[2]=True
                    increment[3]=True
                    for i in range(1,self.size): ##i=1...11
                        for (dx, dy,inc) in ((0, i,0), (i, 0,1), (-i, 0,2), (0, -i,3)): #bottom-right-up-left
                            x=guard[0]+dx
                            y=guard[1]+dy
                            if increment[inc] and 0<=x<self.size and 0<=y<self.size: #in the board
                                if (x,y) in obsticles: #if it is an obstacle
                                    increment[inc]=False #we cannot go further on that direction
                                else: #we didn't hit to an obstacle
                                    #if not in the kings' fields
                                    if not ((x in [self.kings[0][0]-1,self.kings[0][0],self.kings[0][0]+1]  and y in [self.kings[0][1]-1,self.kings[0][1],self.kings[0][1]+1]) or (x in [self.kings[1][0]-1,self.kings[1][0],self.kings[1][0]+1]  and y in [self.kings[1][1]-1,self.kings[1][1],self.kings[1][1]+1])):
                                        move.append(("GM",guard[0],guard[1],x,y)) # that possible action is added to move array
                        if not(increment[0] or increment[1] or increment[2] or increment[3]): # no possible moves on any directions
                            break # immediate break since we are checking from 1 step away at first and incrementing after that
                return move # array of GM,x,y



    def min_path(self,player): # returns the possible escape (no guard) point at the goal row with min dist
        min_val = math.inf
        min_place = [-1,-1]
        for i in range(self.size): #i=0...11
            if not (self.goals[player],i) in self.guards: # if no guard at player's goal row
                if self.distTo[self.v[str(self.goals[player])+","+str(i)]] < min_val:
                    min_val = self.distTo[self.v[str(self.goals[player])+","+str(i)]]
                    min_place[0] = self.goals[player]
                    min_place[1] = i
        return min_place            

    def add_vertices(self,min_lim, max_lim, player):
        self.v = {}
        self.adj = []
        obsticles = []
        place = 0 # will be inceremented to number of (possible) vertices of the player's king
        for (x,y) in self.guards: # for each guards on the board
            for (dx, dy) in ((0, 1), (1, 0), (-1, 0), (0, -1)): # for each 4 sides of the guard
                new_x = x+dx
                new_y = y+dy
                if min_lim <= new_x < max_lim and min_lim <= new_y < max_lim: #if the next point is still in the board (between 0-11)
                    if not new_x == self.goals[player]: #if that point is not at the goal row of the player (if goal is not reached with that move)
                        self.v[str(new_x)+","+str(new_y)] = place # vertex added to dictionary of vertices with its "place" info
                        self.adj.append([])
                        place = place + 1
        for new_y in range(max_lim): # for each points at the goal row of the player (y coordinate kept in newy as 0...11)
            new_x = self.goals[player] # newx = 0 or 11
            if min_lim <= new_x < max_lim and min_lim <= new_y < max_lim: # if the next point is still in the board (between 0-11)
                if (new_x,new_y) not in self.guards: # if at that point there is not a guard on the board
                    self.v[str(new_x)+","+str(new_y)] = place # vertex added to dictionary of vertices with its "place" info
                    self.adj.append([])
                    place = place + 1
        
        self.v[str(self.kings[player][0])+","+str(self.kings[player][1])] = place # the coordinates of the king's position is added to the vertices (its "place" info is equal to the number of vertices-1)
        self.adj.append([])
        keys=list(self.v.keys())
        keys.sort(key=self.sortX)
        obsticles.extend(self.guards) # all the guards on the board are added to the obstacles
        obsticles.append(self.kings[(player+1)%2]) # other player's king is added to the obstacles
        obsticles.sort()
        from_e = keys[0].split(",")
        from_e=[int(from_e[0]),int(from_e[1])]
        next_e = keys[1].split(",")
        next_e=[int(next_e[0]),int(next_e[1])]
        j=0
        next_place=1
        i=1
        while i <len(keys): # number of vertices
            to_e = keys[i].split(",")
            to_e=[int(to_e[0]),int(to_e[1])]
            if from_e[0] != to_e[0]:
                if next_e==None:  # next vertices to be checked are stored in next_e[0] and next_e[1]
                    break
                from_e[0]=next_e[0]
                from_e[1]=next_e[1]
                next_place=next_place+1
                i=next_place
                if next_place<len(keys):
                    next_e = keys[next_place].split(",")
                    next_e=[int(next_e[0]),int(next_e[1])]
                else:
                    next_e=None
                continue
            
            drop = False
            for k in range(0,len(obsticles)):  # check if there are obstacles between two vertices, the edge will be dropped since it is not connecting
                obs=obsticles[k]
                #if from_e[0] != obs[0] or to_e[1]<=obs[1]: 
                    #j=k
                #    break
                if (from_e[0] == obs[0] and to_e[1]<=obs[1]) or to_e[0] < obs[0]:
                    break
                if from_e[0] == obs[0] and from_e[1]<obs[1]<to_e[1]:
                    #j=k+1
                    drop = True
                    break
            if drop:
                i=i+1
                continue
            if from_e[0] == self.goals[player] and to_e[0] == self.goals[player]:
                i=i+1
                continue
            else:
                if from_e[0] == self.kings[player][0] and from_e[1] == self.kings[player][1]: # if the Kings are the "from" side of an edge they are added
                    if (to_e[0],to_e[1]+1) in self.guards:
                        self.addEdge(from_e,to_e,to_e[1]-from_e[1])
                if to_e[0] == self.kings[player][0] and to_e[1] == self.kings[player][1]:
                    if (from_e[0],from_e[1]-1) in self.guards:
                        self.addEdge(to_e,from_e,to_e[1]-from_e[1])
                else:
                    if (to_e[0],to_e[1]+1) in self.guards:
                        self.addEdge(from_e,to_e,to_e[1]-from_e[1])
                    if (from_e[0],from_e[1]-1) in self.guards:
                        self.addEdge(to_e,from_e,to_e[1]-from_e[1])
            i=i+1
        keys.sort(key=self.sortY)  # vertices are sorted horizontally
        obsticles.sort(key=self.sortY)  # obstacles are sorted horizontally
        from_e = keys[0].split(",")
        from_e=[int(from_e[0]),int(from_e[1])]
        next_e=[int(from_e[0]),int(from_e[1])]
        j=0
        next_place=1
        next_obs=0
        i=1
        while i <len(keys):
            to_e = keys[i].split(",")
            to_e=[int(to_e[0]),int(to_e[1])]
            if from_e[1] != to_e[1]:
                if next_e == None:
                    break
                from_e[0]=next_e[0]
                from_e[1]=next_e[1]
                #next_obs=next_obs+1
                next_place=next_place+1
                #j=next_obs
                i=next_place
                if next_place<len(keys):
                    next_e = keys[next_place].split(",")
                    next_e=[int(next_e[0]),int(next_e[1])]
                else:
                    next_e=None
                continue
            drop = False

            for k in range(0,len(obsticles)):
                obs=obsticles[k]
                #if from_e[1] != obs[1] or to_e[0]<=obs[0]:
                    #if next_e[0]> obs[0]:
                    #    j=k
                #    break
                if (from_e[1] == obs[1] and to_e[0]<=obs[0]) or to_e[1] < obs[1]:
                    break
                if from_e[1] == obs[1] and from_e[0]<obs[0]<to_e[0]:
                    #if next_e[0]> obs[0]:
                    #    j=k
                    drop = True
                    break
            
            if drop:
                i=i+1
                continue
            else:
                if from_e[0] == self.kings[player][0] and from_e[1] == self.kings[player][1]: # if the Kings are the "from" side of an edge they are added
                    if (to_e[0]+1,to_e[1]) in self.guards:
                        self.addEdge(from_e,to_e,to_e[0]-from_e[0])
                if to_e[0] == self.kings[player][0] and to_e[1] == self.kings[player][1]:
                    if (from_e[0]-1,from_e[1]) in self.guards:
                        self.addEdge(to_e,from_e,to_e[0]-from_e[0])
                else:
                    if to_e[0]==self.goals[player]:
                        self.addEdge(from_e,to_e,to_e[0]-from_e[0])
                    elif from_e[0] ==self.goals[player]:
                        self.addEdge(to_e,from_e,to_e[0]-from_e[0])
                    else:
                        if (to_e[0]+1,to_e[1]) in self.guards:
                            self.addEdge(from_e,to_e,to_e[0]-from_e[0])
                        
                        if (from_e[0]-1,from_e[1]) in self.guards:
                            self.addEdge(to_e,from_e,to_e[0]-from_e[0])
            i=i+1
    
    def sortY(self,e):  # used to scan all vertices horizontally to find which vertices can be connected to form an edge
        if type(e)==str:
            e=e.split(",")
        return int(e[1])*100+int(e[0])
    def sortX(self,e):  # used to scan all vertices vertically to find which vertices can be connected to form an edge
        if type(e)==str:
            e=e.split(",")
        return int(e[0])*100+int(e[1])
        
    def addEdge(self,from_e, to_e, weight):  # all edges are added with their "from" , "to" , "w" weight information
        self.adj[self.v[str(from_e[0])+","+str(from_e[1])]].append({"from":from_e[:],"to":to_e[:],"w":weight})
    
    def dijkstra(self,s):
        self.distTo = []  # the distances of the vertices are stored to the source vertex
        self.edgeTo = []  # the edges are stored, in order to return the path to the goal from the source
        for ver in range(len(self.adj)):
            self.distTo.insert(ver, math.inf)
            self.edgeTo.append(None)
        self.distTo[s]= 0.0
        self.pq = PriorityQueue()
        self.pq.put((self.distTo[s],s))
        while not self.pq.empty():   # while the priority queue is not empty
            ver=self.pq.get()
            for e in self.adj[ver[1]]:
                self.relax(e)

    def relax(self,e):
        v = self.v[str(e["from"][0])+","+str(e["from"][1])]
        w = self.v[str(e["to"][0])+","+str(e["to"][1])]
        if self.distTo[w] > self.distTo[v] + e["w"]:  # if the current calculated distance is larger than distance to "v" + new edge weight
            self.distTo[w] = self.distTo[v] + e["w"]  # update the distance information with the improved (smaller) one
            self.edgeTo[w] = e
            found =[x for x in self.pq.queue if x[1]==w]
            if len(found)!=0:
                self.pq.queue.remove(found[0])
                heapq.heapify(self.pq.queue)
                self.pq.put((self.distTo[w], w))
            else:
                self.pq.put((self.distTo[w],w))

    def hasPathTo(self, v):
        return self.distTo[v] < math.inf
    
    def is_finished(self):
        """Return whether no more moves can be made (i.e.,
        game finished).
        """
        return self.kings[0][0]==self.goals[0] or self.kings[1][0]==self.goals[1]
        

    def get_score(self, player=PLAYER1):
        """Return a score for this board for the given player.

        The score is the difference between the lengths of the shortest path
        of the player minus the one of its opponent.
        """
        score = self.min_steps_before_victory(player)-self.min_steps_before_victory((player+1)%2)  
        
        return score
    def min_steps_before_victory(self,player=PLAYER1): # returns the distance from the destination for the winning player
        kings_init = [(1, 7), (10, 4)]
        if self.kings[player][0]==self.goals[player]:
            board=self.clone()
            board.kings[player]=kings_init[player]
            board.add_vertices(0,board.size,player) #min_lim=0, max_lim=12
            board.dijkstra(board.v[str(board.kings[player][0])+","+str(board.kings[player][1])])  # call dijkstra to get minimum path and backtrack from the goal to the players king
            if board.hasPathTo(board.v[str(self.kings[player][0])+","+str(self.kings[player][1])]):
                return board.distTo[board.v[str(self.kings[player][0])+","+str(self.kings[player][1])]]  # if the player has not won 0 is returned and the game continues
        else:
            return 0
        
        #if self.kings[player][0]==self.goals[player]:
        #     return 0
        #self.add_vertices(0,self.size,player) #min_lim=0, max_lim=12
        #self.dijkstra(self.v[str(self.kings[player][0])+","+str(self.kings[player][1])])
        #for i in range(self.size):
        #    if not (self.goals[player],i) in self.guards:
        #        if self.hasPathTo(self.v[str(self.goals[player])+","+str(i)]):
        #            return 1
        #return 10

    def utility(self,player):
        score = self.get_score(player)
        if self.kings[player][0]==self.goals[player]:  # if the player wins (player is at the goal row) return value is 100
            return 100
        if self.kings[(player+1)%2][0]==self.goals[(player+1)%2]:  # if the opponent wins (opponent is at the goal row) return value is -100
            return -100
        # calculate player's score by finding the possible closest move to the goal row of the player
        self.add_vertices(0,self.size,player) # min_lim=0, max_lim=12
        self.dijkstra(self.v[str(self.kings[player][0])+","+str(self.kings[player][1])])  # dijkstra method is used to find the all possible paths for player
        keys = list(self.v.keys())  # keys (location i.e x and y values- row and column numbers) of each possible locations assigned to keys for player
        min_val = self.size  # initially assigned as 12 (size of the board)
        for i in range(len(self.v)):  # iterate through all possible path to find the closest move to the goal row for player
            key=keys[i].split(",")  # row and column values retrieved for player
            key= (int(key[0]),int(key[1]))  # row and column values converted to integer value with int() cast for player
            if self.distTo[self.v[keys[i]]]<math.inf and min_val>abs(self.goals[player]- key[0]):  # if there is valid path to the given location and the given location is closer to the goal row
                min_val =abs(self.goals[player]- key[0])  # update the value of min_val with closer point to goal row for player
        score_of_player = self.size-min_val   # player's score calculated by difference (distance) between the size of the board and the move which brings player to the closest point to the goal row of the player

        # calculate opponents's score by finding the possible closest move to the goal row of the opponent
        self.add_vertices(0,self.size,(player+1)%2) # min_lim=0, max_lim=12
        self.dijkstra(self.v[str(self.kings[(player+1)%2][0])+","+str(self.kings[(player+1)%2][1])])  # dijkstra method is used to find the all possible paths for opponent
        keys = list(self.v.keys())  # keys (location i.e x and y values- row and column numbers) of each possible locations assigned to keys for opponent
        min_val = self.size  # initially assigned as 12 (size of the board)
        for i in range(len(self.v)):  # iterate through all possible path to find the closest move to the goal row for opponent
            key=keys[i].split(",")  # row and column values retrieved
            key= (int(key[0]),int(key[1]))  # row and column values converted to integer value with int() cast for opponent
            if self.distTo[self.v[keys[i]]]<math.inf and min_val>abs(self.goals[(player+1)%2]- key[0]):  # if there is valid path to the given location and the given location is closer to the goal row
                min_val =abs(self.goals[(player+1)%2]- key[0])  # update the value of min_val with closer point to goal row for player
        score_of_opponent = self.size-min_val  # opponent's score calculated by difference (distance) between the size of the board and the move which brings opponent to the closest point to the goal row of the opponent
        return score_of_player - score_of_opponent  # return the difference between the player's score and opponent's score to the min_val() or max_val() function under alpha_beta_search() method in alphabeta_agent.py




    
def dict_to_board(dictio):
    """Return a clone of the board object encoded as a dictionary."""
    clone_board = Board()
    clone_board.kings[0] = dictio['kings'][0]
    clone_board.goals[0] = dictio['goals'][0]
    clone_board.kings[1] = dictio['kings'][1]
    clone_board.goals[1] = dictio['goals'][1]
    for (x, y) in dictio['guards']:
        clone_board.guards.append((x, y))

    clone_board.nb_guards[0] = dictio['nb_guards'][0]
    clone_board.nb_guards[1] = dictio['nb_guards'][1]
    return clone_board


def load_percepts(csvfile):
    """Load percepts from a CSV file.

    Cells are hexadecimal numbers.

    """
    if isinstance(csvfile, str):
        with open(csvfile, "r") as f:
            return load_percepts(f)
    else:
        import csv
        percepts = []
        for row in csv.reader(csvfile):
            if not row:
                continue
            row = [int(c.strip(), 16) for c in row]
            percepts.append(row)
            assert len(row) == len(percepts[0]), \
                "rows must have the same length"
        return percepts


class Agent:
    """Interface for a Blockade agent"""

    def initialize(self, percepts, players, time_left):
        """Begin a new game.

        The computation done here also counts in the time credit.

        Arguments:
        percepts -- the initial board in a form that can be fed to the Board
            constructor.
        players -- sequence of players this agent controls
        time_left -- a float giving the number of seconds left from the time
            credit for this agent (all players taken together). If the game is
            not time-limited, time_left is None.

        """
        pass

    
    def play(self, percepts, player, step, time_left):
        """Play and return an action.

        Arguments:
        percepts -- the current board in a form that can be fed to the Board
            constructor.
        player -- the player to control in this step
        step -- the current step number, starting from 1
        time_left -- a float giving the number of seconds left from the time
            credit. If the game is not time-limited, time_left is None.

        """

        pass

