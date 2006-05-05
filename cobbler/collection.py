import serializable

"""
Base class for any serializable lists of things...
"""
class Collection(serializable.Serializable):

    def class_container(self):
        raise exceptions.NotImplementedError

    def filename(self):
        raise exceptions.NotImplementedError

    def __init__(self,config):
        """
	Constructor.
	"""
        self.config = config
        self.clear()
        

    def clear(self):
        self.listing = {}

    def find(self,name):
        """
        Return anything named 'name' in the collection, else return None if
        no objects can be found.
        """
        if name in self.listing.keys():
            return self.listing[name]
        return None


    def to_datastruct(self):
        """
        Serialize the collection
        """
        datastruct = [x.to_datastruct() for x in self.listing.values()]

    def from_datastruct(self,datastruct):
        container = self.class_container()
        for x in datastruct:
            item = container(x,self.config)
            self.add(item)

    def add(self,ref):
        """
        Add an object to the collection, if it's valid.  Returns True
        if the object was added to the collection.  Returns False if the
        object specified by ref deems itself invalid (and therefore
        won't be added to the collection).
        """
        if ref is None or not ref.is_valid():
            if utils.last_error() is None or utils.last_error() == "":
                utils.set_error("bad_param")
            return False
        self.listing[ref.name] = ref
        return True


    def printable(self):
        """
        Creates a printable representation of the collection suitable
        for reading by humans or parsing from scripts.  Actually scripts
        would be better off reading the YAML in the config files directly.
        """
        values = map(lambda(a): a.printable(), sorted(self.listing.values()))
        if len(values) > 0:
           return "\n\n".join(values)
        else:
           return m("empty_list")

    def __iter__(self):
        """
	Iterator for the collection.  Allows list comprehensions, etc
	"""
        for a in self.listing.values():
	    yield a

    def __len__(self):
        """
	Returns size of the collection
	"""
        return len(self.listing.values())

