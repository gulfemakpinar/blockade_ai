from blockade import *
import random 
import time
import math
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
        self.players=players
        self.time_left = time_left
        self.initial = Board(percepts=percepts)
    
    def play(self, percepts, player, step, time_left):
        #action to be played is searched and found and decided
        """Play and return an action.

        Arguments:
        percepts -- the current board in a form that can be fed to the Board
            constructor.
        player -- the player to control in this step
        step -- the current step number, starting from 1
        time_left -- a float giving the number of seconds left from the time
            credit. If the game is not time-limited, time_left is None.

        """
        
        if time_left ==None:
            time_left=30 #time limit for an action
        start = time.time()
        state = Board(percepts=percepts)
        if state.kings[(player+1)%2][0] != self.initial.kings[(player+1)%2][0] or state.kings[(player+1)%2][1] != self.initial.kings[(player+1)%2][1]: #if king has made a move
            self.initial.play_action(("K",state.kings[(player+1)%2][0],state.kings[(player+1)%2][1]),(player+1)%2) #the action of the king is added to the initial board
        else: #if there are not any king moves (to check the G or GM actions made)
            added = (-1,-1)
            deleted = (-1,-1)
            for guard in state.guards: #for each guard at the state of the board
                if not guard in self.initial.guards:
                    added=guard #it is a new action (new position of the guard)
            for guard in self.initial.guards: #for each guard at the initial board
                if not guard in state.guards:
                    deleted=guard #guard is moved from that location
            '''
            state.guards.sort()
            self.initial.guards.sort()
            print(state.guards)
            print(self.initial.guards)
            added =(-1,-1)
            deleted =(-1,-1)
            i=0
            j=0
            while i <len(state.guards):
                print(i,j)
                if i+1>=len(state.guards) and j+1<len(self.initial.guards) and deleted==(-1,-1):
                    deleted =  self.initial.guards[j]
                    break
                if len(self.initial.guards)!=0:
                    if j<len(self.initial.guards):
                        if state.guards[i] != self.initial.guards[j]:
                            if j+1<len(self.initial.guards):
                                if  state.guards[i] == self.initial.guards[j+1]:
                                    deleted =  self.initial.guards[j]
                                    j=j+1
                                    continue
                            
                            if i+1<len(state.guards):
                                if  state.guards[i+1] == self.initial.guards[j]:
                                    added =  state.guards[i]
                                    i=i+1
                                    continue
                            if j+1<len(self.initial.guards) and i+1<len(state.guards):
                                if  state.guards[i+1] == self.initial.guards[j+1]:
                                    deleted =  self.initial.guards[j]
                                    added =  state.guards[i]
                                    i=i+1
                                    j=j+1
                                    continue
                            elif j+1>=len(self.initial.guards) and i+1>=len(state.guards):
                                deleted =  self.initial.guards[j]
                                added =  state.guards[i]
                                break
                            if j+1>=len(self.initial.guards):
                                added =  state.guards[i]
                                break
                    else:
                        added =  state.guards[i]
                        break
                else:
                    added =  state.guards[i]
                    break
                i=i+1
                j=j+1'''
            if added !=(-1,-1): #if there is any change on the guard positions
                if deleted !=(-1,-1): #guard is moved
                    self.initial.play_action(("GM",deleted[0],deleted[1],added[0],added[1]),(player+1)%2)
                else: #new guard is placed
                    self.initial.play_action(("G",added[0],added[1]),(player+1)%2)
        
        state=self.initial.clone() #the current state is assigned as the initial state of the board
        depth_limit = 1 #to apply the ITERATIVE DEEPENING IMPROVEMENT depth is started at 1(limit)... till 30 sn
        stored_mov=None
        while True:
            mov,okay=self.alpha_beta_search(state,player,start,time_left,depth_limit) #alpha beta search with cutoff
            depth_limit=depth_limit+1
            '''end = time.time()
            t = end - start'''
            if okay: #if we reach the time limit (30sn) 
                break
            else:  #if we did not reach the time limit (30sn) 
                stored_mov=mov
        self.initial.play_action(stored_mov,player) #move found is played on initial board
        end = time.time() #time printed
        t = end - start #elapsed time is calculated
        '''global is_gm
        global guard_location
        if stored_mov[0]=="GM":
            guard_location = (stored_mov[1],stored_mov[1])
            is_gm = True
            stored_mov=(stored_mov[0],stored_mov[3],stored_mov[4])'''
        print(t)
        print(stored_mov)
        return stored_mov

    def alpha_beta_search(self,state,player,time_s, time_left,depth_limit):

        def cache_state(func):
            cache = {} # results are saved here
            def wrapped(x,*args): # the caching is done based on the state "x", not on the values of alpha and beta
                if x not in cache:
                    cache[x] = func(x,*args)
                return cache[x]
            return wrapped
        
        @cache_state #CACHE IMPROVEMENT
        def max_value(state, alpha, beta, ply, depth,time_lef):
            if state.is_finished() or depth == depth_limit: #check if the game is finished or depth limit is reached
                temp_time = time.time()
                t=temp_time-time_s
                if time_lef-1<t: #if time limit is reached 
                    return state.utility(player), None, True # if the time limit has been reaached None and True are returned
                else:
                    return state.utility(player), None, False # continues to search with utility function
            v, move = -math.inf, None
            acts =state.actions(ply) #legal actions are assigned to act
            if acts != None:
                random.shuffle(acts) #legal actions are randomized to improve alpha beta pruning
            for a in acts: #for each legal possible actions of a player
                temp_time = time.time()
                t=temp_time-time_s
                if time_lef-1<t: #if time limit is reached 
                    return 0, None, True #the time limit has been reached
                v2, _,okay = min_value(state.clone().play_action( a, ply), alpha, beta, (ply+1)%2,depth+1,time_lef) #legal action is played and min_value func is called
                 #ALPHA BETA PRUNING
                if v2 > v:
                    v, move = v2, a
                    alpha = max(alpha, v)
                if v >= beta:
                    temp_time = time.time()
                    t=temp_time-time_s
                    if time_lef-1<t:
                        return v, move, True
                    else:
                        return v, move, okay
            temp_time = time.time()
            t=temp_time-time_s
            if time_lef-1<t:  #if time limit is reached 
                return v, move, True
            else:
                return v, move, False

        @cache_state #CACHE IMPROVEMENT
        def min_value(state, alpha, beta, ply, depth,time_lef):
            #similar operations are done at the max_value function, instead action with min_value will be found 
            if state.is_finished() or depth == depth_limit:
                temp_time = time.time()
                t=temp_time-time_s
                if time_lef-1<t:
                    return state.utility(player), None, True
                else:
                    return state.utility(player), None, False
            v, move = +math.inf, None
            acts =state.actions(ply)
            if acts != None:
                random.shuffle(acts)
            for a in acts:
                temp_time = time.time()
                t=temp_time-time_s

                if time_lef-1<t:
                    return 0, None, True
                v2, _,okay = max_value(state.clone().play_action( a, ply), alpha, beta,(ply+1)%2,depth+1,time_lef)
                
                if v2 < v:
                    v, move = v2, a
                    beta = min(beta, v)
                if v <= alpha:
                    temp_time = time.time()
                    t=temp_time-time_s
                    if time_lef-1<t:
                        return v, move, True
                    else:
                        return v, move, okay
                        
            temp_time = time.time()
            t=temp_time-time_s
            if time_lef-1<t:
                return v, move, True
            else:
                return v, move, False
        _, mov, okay = max_value(state, -math.inf, +math.inf, player,0,time_left)
        return mov,okay #FOUND ACTION IS RETURNED


def serve_agent(agent, address, port):
    """Serve agent on specified bind address and port number."""
    from xmlrpc.server import SimpleXMLRPCServer
    server = SimpleXMLRPCServer((address, port), allow_none=True)
    server.register_instance(agent)
    print("Listening on ", address, ":", port, sep="")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def agent_main(agent, args_cb=None, setup_cb=None):
    """Launch agent server depending on arguments.

    Arguments:
    agent -- an Agent instance
    args_cb -- function taking two arguments: the agent and an
        ArgumentParser. It can add custom options to the parser.
        (None to disable)
    setup_cb -- function taking three arguments: the agent, the
        ArgumentParser and the options dictionary. It can be used to
        configure the agent based on the custom options. (None to
        disable)

    """
    import argparse

    def portarg(string):
        value = int(string)
        if value < 1 or value > 65535:
            raise argparse.ArgumentTypeError("%s is not a valid port number" %
                                             string)
        return value

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bind", dest="address", default="",
                        help="bind to address ADDRESS (default: *)")
    parser.add_argument("-p", "--port", type=portarg, default=8000,
                        help="set port number (default: %(default)s)")
    if args_cb is not None:
        args_cb(agent, parser)
    args = parser.parse_args()
    if setup_cb is not None:
        setup_cb(agent, parser, args)

    serve_agent(agent, args.address, args.port)


agent = Agent()
agent_main(agent)