
class Item(object):
    def __init__(self):
        self.name = "Default item"
        self.description = "Default item description"

    def use(self):
        print("item",self.name,"used")
