from collections import namedtuple

Person = namedtuple("Person", "name children")
john = Person("John Doe", ["Timmy", "Jimmy"])
Person(name='John Doe', children=['Timmy', 'Jimmy'])
print(john.children)

john.children.append("Tina")
Person(name='John Doe', children=['Timmy', 'Jimmy', 'Tina'])
print(john.children)