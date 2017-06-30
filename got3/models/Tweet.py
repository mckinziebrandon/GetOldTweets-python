DEFAULT_ATTRIBUTES = [
        'sender',
        'receiver',
        'date',
        'text',
        'id',
        'permalink'
        ]


class Tweet:

    def __init__(self):
        self.__dict__['params'] = {attr: None for attr in DEFAULT_ATTRIBUTES}

    def __repr__(self):
        return str(self.__dict__['params'])

    def __iter__(self):
        return self.__dict__['params'].__iter__()

    def as_dict(self):
        """smh"""
        return self.__dict__['params']

    def __getattr__(self, name):
        if name in self.__dict__['params']:
            return self.__dict__['params'][name]
        else:
            raise AttributeError('Attribute {} not found'.format(name))

    def __setattr__(self, name, value):
        super(Tweet, self).__setattr__(name, value)
        if name in DEFAULT_ATTRIBUTES:
            self.__dict__['params'][name] = value




