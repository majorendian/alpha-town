
# global events taking place

class EventHandler(object):
    def __init__(self):
        self.register = {}

    def bind(self, event_name, callback):
        if not event_name in self.register:
            self.register[event_name] = []
        self.register[event_name].append(callback)

    def emit(self, event_name, *args, **kwargs):
        if event_name in self.register:
            for cb in self.register[event_name]:
                cb(*args, **kwargs)
        else:
            raise Exception("No such event: "+event_name)
                
