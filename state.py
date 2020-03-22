
# Main state object

class State(object):
    def __init__(self, fsm):
        self.fsm = fsm
        self.verbose = True

    def run(self):
        assert 0, "run() not implemented"

    def enter(self):
        if self.verbose:
            print("Entering state:"+str(type(self)))
        # assert 0,"enter() not implemented"

    def leave(self):
        if self.verbose:
            print("Leaving state:"+str(type(self)))
        # assert 0,"leave() not implemented"

# Transition object. Transitions are in the form of FromAStateToBState_Transition to organize
# various transitions from various other transitions so that the flow control is under tight
# monitoring.
# from_state must match cur_state in the FSM to execute, otherwise an error is thrown

class Transition(object):
    def __init__(self, fsm, from_state, to_state):
        self.fsm = fsm
        self.from_state = from_state
        self.to_state = to_state

    def execute(self):
        assert 0, "execute() not implemented"


# We need the simple transition for certain purposes where we do not necessarily care what kind of state the object was in
# previously, we can use the simple_transition(...) function to achive this effect given we inherit from the following class
class SimpleTransition(object):
    def __init__(self, fsm, to_state):
        self.fsm = fsm
        self.to_state = to_state

    def execute(self):
        assert 0, "execute() not implemented"
# Keeps track of states

class StateMachine(object):
    def __init__(self):
        self.states = {}
        self.transitions = {}
        self.cur_state = None
        self.prev_state = None
        self.trans = None

    def set_state(self, state_name):
        self.prev_state = self.cur_state
        self.cur_state = self.states[state_name]
    def get_state(self):
        return self.cur_state

    def transition(self, trans_name):
        self.trans = self.transitions[trans_name]
        assert type(self.states[self.trans.from_state]) == type(self.cur_state), "Can't transition to "+str(type(self.states[self.trans.to_state]))+" from "+str(type(self.states[self.trans.from_state]))+" because it doesn't match the current state "+str(type(self.cur_state))

    # the simple transition will make sure we can transition from any state to the specified state
    def simple_transition(self, trans_name):
        self.trans = self.transitions[trans_name]
        assert isinstance(self.trans, SimpleTransition), type(self.trans) + " is not a simple type of transition"

    def run(self):
        if self.trans:
            self.cur_state.leave()
            #NOTE: if self.trans.execute() transitions into another state, that new trans.execute() function may not run
            self.trans.execute()
            self.set_state(self.trans.to_state)
            self.cur_state.enter()
            self.trans = None
        self.cur_state.run()
        
        
