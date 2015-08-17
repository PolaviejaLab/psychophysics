import re
import uuid


class Template:
    def __init__(self, name):
        self.file = open(name)
        self.data = self.file.read()

        pairs = dict()
        pairs['RANDOM_UUID'] = lambda x: str(uuid.uuid4())

        self.replace(pairs)


    def replace(self, pairs):
        for key in pairs:
            value = pairs[key]
            self.data = re.sub("(@" + key + "@)", value, self.data)

    def write(self, name):
        file = open(name, "w")
        file.write(self.__str__())
        file.close()

    def __str__(self):
        return self.data
