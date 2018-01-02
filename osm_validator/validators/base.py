import os

_validators = []


class BaseValidator(object):

    def __init__(self, *args, **kwargs):
        pass

    async def init(self):
        pass

    async def prepare(self, change):
        pass

    async def check(self, change):
        pass


class Validator(BaseValidator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instances = []
        for validator in _validators:
            instance = validator(*args, **kwargs)
            self._instances.append(instance)

    async def init(self, ignore=frozenset()):
        all_new = []
        for instance in self._instances:
            if instance.handle in ignore:
                continue
            new = await instance.init()
            all_new.extend(new)
        return all_new

    async def prepare(self, change):
        for instance in self._instances:
            await instance.prepare(change)

    async def check(self, change):
        all_new = []
        all_fixed = []
        for instance in self._instances:
            new, fixed = await instance.check(change)
            all_new.extend(new)
            all_fixed.extend(fixed)
        return all_new, all_fixed


def register(cls):
    _validators.append(cls)
    return cls


def load_validators():
    main = os.path.dirname(__file__)
    for root, folders, files in os.walk(main):
        if root == main or '__init__.py' not in files:
            continue
        __import__('.'.join(
            __name__.split('.')[:-1] + os.path.relpath(root, main).split(os.path.sep))
        )


load_validators()
