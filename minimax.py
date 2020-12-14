
class Node:
    def __init__(self, depth, data=None, childs=[]):
        self.__data = data
        self.__childs = childs
        self.__depth = depth

    def data(self):
        return self.__data

    def childs(self):
        return self.__childs

    def addChild(self,child):
        self.__childs.append(child)

    def getDepth(self):
        return self.__depth

    def clearChilds(self):
        self.__childs = []
