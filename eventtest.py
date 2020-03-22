from pydispatch import Dispatcher

class MyEmitter(Dispatcher):
    # Events are defined in classes and subclasses with the '_events_' attribute
    _events_ = ['on_state', 'new_data']
    def do_some_stuff(self):
        # do stuff that makes new data
        data = "TEST"
        # Then emit the change with optional positional and keyword arguments
        self.emit('new_data', data=data)

# An observer - could inherit from Dispatcher or any other class
class MyListener(object):
    def on_new_data(self, *args, **kwargs):
        data = kwargs.get('data')
        print('I got data: {}'.format(data))
    def on_emitter_state(self, *args, **kwargs):
        print('emitter state changed')

emitter = MyEmitter()
listener = MyListener()

emitter.bind(on_state=listener.on_emitter_state)
emitter.bind(new_data=listener.on_new_data)

emitter.do_some_stuff()
# >>> I got data: ...

emitter.emit('on_state')
# >>> emitter state changed
