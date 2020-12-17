class Sim:
  def __init__(self, val, mv, spc):
    self.move = mv
    self.score = val
    self.special = spc
    self.childs = []
    
  def addChild(self,otherSim):
  	self.childs.append(otherSim)

  def getMove(self):
    return self.move

  def getData(self):
    return self.score

  def getSpecial(self):
    return self.special

  def getChilds(self):
    return self.childs

  def orderChilds(self):
    self.childs = (sorted(self.getChilds(), key=lambda sim: sim.getData()))

  def clearChilds(self):
    self.childs = []

  def showTree(self,depth):
    s = ''
    s += '{} {}-{}-{} : {}\n'.format(' '*depth, depth, self.getMove(), self.getSpecial(), self.getData())
    for child in self.childs:
        s += child.showTree(depth+1)
    return s


# Test
"""
AI_color = 'black'

def oppositeColor(color):
    if color == 'black':
        return 'white'
    return 'black'

def minimax(_head,_color,_depth,maxDepth,alert=False):    

    if _depth == maxDepth:
        # bottom elements
        return _head.getData()
    else:

        advantages = []
        childs = _head.getChilds()
        for child in childs:
            temp_minimax = minimax(child,oppositeColor(_color),(_depth+1),maxDepth) 
            advantages.append(temp_minimax)


        if _color == AI_color:
            # Highest score
            max_advantage = max(advantages)
            toTransferIndex = advantages.index(max_advantage)
        else:
            # Lowest score
            min_advantage = min(advantages)
            toTransferIndex = advantages.index(min_advantage)

        if _depth == 0:
            return childs[toTransferIndex].getMove()
        else:
            return advantages[toTransferIndex]





if __name__ == '__main__':
    
    head = Sim(9,str(9)+'MOVE')

    s1 = [-2,3]

    for v in s1:
        temp = Sim(v,str(v)+'MOVE')
        head.addChild(temp)

    e1 = head.getChilds()

    # child 1
    s2 = [4,2]
    main1 = e1[0]
    for v in s2:
        temp = Sim(v,str(v)+'MOVE')

        main1.addChild(temp)

    # child2
    s2 = [-1,8]
    main2 = e1[1]

    for v in s2:
        temp = Sim(v,str(v)+'MOVE')

        main2.addChild(temp)

    print([x.getData() for x in e1])
    print([x.getData() for x in main1.getChilds()])
    print([x.getData() for x in main2.getChilds()])

    
    res = minimax(head,'black',0,2)
    print(res)

"""