import item

class Recipie(object):
    def __init__(self):
        self.name = None
        self.required_items = None
        self.gives_item = None

class WoodenWallRecipie(Recipie):
    def __init__(self):
        super().__init__()
        self.name = "Wooden Wall"
        self.required_items = [ {"item":item.Wood, "count": 3} ]
        self.gives_item = item.WoodenWall
        
