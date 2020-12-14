import chess
import chess.svg
import random
import matplotlib.pyplot as plt
from minimax import *

import theorical_position_advantage as ENGINE_ADV_POSITION
from LichessComparator import LichessComparator

pieceTypes = [
    'PAWN',
    'KNIGHT',
    'BISHOP',
    'ROOK',
    'QUEEN',
    'KING'
]

SCORETABLE_values = {
    'PAWN':      1,
    'KNIGHT':    3,
    'BISHOP':    3,
    'ROOK':      5,
    'QUEEN':     10,
    'KING':      9
}

FORMULA = {
    "pieceValue": 2,
    "theorical_position": 0.1,
    "maxVictimValue": 0.5,
    "case_protected": 0.1,
    "nbThreats": 0.4
}


class Analyzer:

    def __init__(self,AI_color):
    
        if AI_color == 'black':
            self.AI_color = True
            self.AI_color_expl = 'black'
            self.AI_color_expl_op = 'white'
        else:
            self.AI_color = False
            self.AI_color_expl = 'white'
            self.AI_color_expl_op = 'black'
        

        self.__board = chess.Board()

    def getPlayingColor(self):
        if self.__board.turn:
            return self.AI_color_expl
        else:
            return self.AI_color_expl_op

    def setPlayingColor(self,color):
        # To be tested
        if color != self.AI_color_expl:
            self.__board.turn = True
        else:
            self.__board.turn = False


    def setFEN(self,fen):
        self.__board.set_fen(fen)

    def getFEN(self):
        return self.__board.fen()

    def getResult(self):
        res = str(self.__board.result())
        if self.isGameOver():
            res = res.split('-')
            if res[0] == '1/2':
                res[0] = eval(res[0])
                res[1] = eval(res[1])
            return {'white':float(res[0]), 'black': float(res[1])}
        else:
            return {'white':None, 'black': None}

    def isGameOver(self):
        return self.__board.is_game_over()

    def isCheckmate(self):
        return self.__board.is_checkmate()

    def saveBoard(self,s):
        boardsvg = chess.svg.board(board=self.__board)
        f = open("boards/board"+str(s)+".SVG", "w")
        f.write(boardsvg)
        f.close()

    def drawBoard(self,s,isBigChange=False):
        print(self.__board.unicode())

    def getLegalMoves(self):
        return self.__board.legal_moves

    def move(self,m):
        self.__board.push(m)
    
    def back(self):
        self.__board.pop()

    def getPieceValueFromType(self,pieceType):
        pieceValue = SCORETABLE_values[pieceType]
        return pieceValue

    def generateMoveScore(self,moveData,pieceColor):
        
        pieceType = moveData["type"]
        piecePosition = moveData["position"]
        pieceAttacks = moveData["attacks"]
        pieceAttackers = moveData["attackers"]

        # This piece's value
        pieceValue = self.getPieceValueFromType(pieceType)
        
        # Possible attacks
        maximumVictimValue = 0
        if len(pieceAttacks) != 0:
            victimsValues = []
            for victim in pieceAttacks:
                victimType = self.__board.piece_type_at(victim)
                if victimType != None:
                    victimsValues.append(self.getPieceValueFromType(pieceTypes[victimType-1]))

            if len(victimsValues) != 0:
                maximumVictimValue = sum(victimsValues)

        # Threats
        nbThreats = len(pieceAttackers)
        """
        I should implement a way to verify if the case is protected and if the attackers are less valuable than this piece or not
        """
        

            
        """
        Piece Value
        Maximum Gain
        - number of threats
        """

        formulaResult = + FORMULA["pieceValue"] * pieceValue                                                            \
                        + FORMULA["theorical_position"] * ENGINE_ADV_POSITION.raw(piecePosition, pieceType, pieceColor) \
                        + FORMULA["maxVictimValue"] * maximumVictimValue                                                \
                        - FORMULA["nbThreats"] * nbThreats                                                              \

        if pieceType == "KING":
            formulaResult -= pieceValue
                               

        return formulaResult

    def getBoardDetails(self):
        boardData = {
            'black': [],
            'white': []
        }

        # Simulate both players
        self.setPlayingColor(self.AI_color_expl)
        legal_moves = list(self.getLegalMoves())

        self.setPlayingColor(self.AI_color_expl_op)
        legal_moves = legal_moves + list(self.getLegalMoves())



        legal_moves_starter = [m.uci()[0:2] for m in legal_moves]
        legal_moves_ender = [m.uci()[2:4] for m in legal_moves]

        for i in range(64):
            pieceType = self.__board.piece_type_at(i)
            pieceColor = self.__board.color_at(i)
            piecePosition = chess.square_name(i)

            if pieceColor != None:
                if pieceColor:
                    pieceClass = self.AI_color_expl_op
                else:
                    pieceClass = self.AI_color_expl
                                    
                possibleVictims = [a for a in list(self.__board.attacks(i)) if self.__board.piece_at(a) != None and self.__board.piece_at(a).color != pieceColor]
                possibleAttackers = [a for a in list(self.__board.attackers(pieceColor,chess.parse_square(piecePosition))) if self.__board.piece_at(a).color != pieceColor]

                boardData[pieceClass].append({
                    'type': pieceTypes[pieceType-1],
                    'position': piecePosition,
                    'attacks': possibleVictims,
                    'attackers': possibleAttackers
                })
            
        return boardData

    def reset(self):
        self.__board.reset()

def fillSize(lst,size):
    while len(lst) != size:
        lst.append(lst[0])
    
    return lst


def correctSize(lst,size):
    while len(lst) != size:
        lst.append(None)
    
    return lst

def oppositeColor(color):
    if color == 'black':
        return 'white'
    return 'black'

def getScoreFromSimulatedBoard(Analyzer,colorToPlay,AI_color,AI_OP_color):
    # Get board details
    moves = Analyzer.getBoardDetails()

    # Reset the playing color
    Analyzer.setPlayingColor(colorToPlay)

    # AI moves
    AI_Moves = moves[AI_color]
    AI_score = 0
    for moveIndex,moveData in enumerate(AI_Moves):
        AI_score += (Analyzer.generateMoveScore(moveData,AI_color))

    # AI-Opposite moves
    AI_OP_Moves = moves[AI_OP_color]
    AI_OP_score = 0
    for moveIndex,moveData in enumerate(AI_OP_Moves):
        AI_OP_score += (Analyzer.generateMoveScore(moveData,AI_OP_color))
    
    # AI advantage
    if AI_color == 'black':
        AI_Advantage = AI_score - AI_OP_score
    else:
        AI_Advantage = AI_OP_score - AI_score

    return AI_Advantage
    

MEMORY_AI_Advantages_BIGTEST = []

AI_color = 'white'
AI_OP_color = 'black'

Analyzer = Analyzer(AI_color)

PARAM_CompareToLichess = False
PARAM_ConsoleSteps = False
PARAM_ConsoleBoard = False
PARAM_ConsoleBigTest = False
PARAM_BigTest = False
PARAM_BigTest_count = 100
PARAM_randomAI_OP_Moves = True
PARAM_maxTurn = 50
PARAM_ColorToPlay = 'white'
PARAM_Depth = 1
TEMP_calculatedScenarios = 0

def generateScoreTree(Analyzer,_head,_color,_depth):
    global TEMP_calculatedScenarios

    if _depth > 0:

        legalsMoves = list(Analyzer.getLegalMoves())
        for move in legalsMoves:
            # Get the correct color
            simulatedColor = oppositeColor(_color)
            # Simulate move
            Analyzer.move(move)
            # Results
            res = Analyzer.getResult()
            specialTreatement = None
            if res[AI_color] == 1.0:
                specialTreatement = True
            elif res[AI_color] == 0.0:
                specialTreatement = False

            # Getting the score
            score = getScoreFromSimulatedBoard(Analyzer,simulatedColor,AI_color,AI_OP_color)
            TEMP_calculatedScenarios += 1
            if TEMP_calculatedScenarios % 1000 == 0:
                print(TEMP_calculatedScenarios)

            # Create node
            child = Node(0,[
                score,
                simulatedColor,
                move,
                specialTreatement
            ])
            
            generateScoreTree(Analyzer,child,simulatedColor,(_depth-1))

            Analyzer.back()

            _head.addChild(child)

def minimax(_head,_color,_depth,maxDepth,alert=False):    

    if _depth == maxDepth:
        # bottom elements
        return _head.data()[0]
    else:

        advantages = []
        childs = _head.childs()
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
            #print(min_advantage)

        if _depth == 0:
            return childs[toTransferIndex].data()[2]
        else:
            return advantages[toTransferIndex]

            


    







def Simulation():


    MEMORY_AI_Advantages = []
    MEMORY_Lichess_Advantages = []

    colorToPlay = PARAM_ColorToPlay

    s = 0
    nb_moves = PARAM_maxTurn


    # Start the lichess comparator
    if PARAM_CompareToLichess:
        instance = LichessComparator(AI_color,True)
        isConnected = instance.connectToLichess()
        print('Lichess Comparator connection: {}'.format(isConnected))

    # Reset Board
    Analyzer.reset()

    # Test FEN
    Analyzer.setFEN('r2qkbnr/pppppp1p/6p1/3b1n2/8/3B3N/PPPPPPPP/RNQB1K1R w KQkq - 0 1')





    while not Analyzer.isGameOver() and s < nb_moves:
        
        # Actual board configuration score generator
        AI_Advantage = getScoreFromSimulatedBoard(Analyzer,colorToPlay,AI_color,AI_OP_color)

        ## Graph data collector
        MEMORY_AI_Advantages.append(AI_Advantage)

        # Lichess score comparator
        actualFEN = Analyzer.getFEN()
        if PARAM_CompareToLichess:
            lichessScore = instance.getScore(actualFEN)
            MEMORY_Lichess_Advantages.append(lichessScore)


        # Use minimax to select a move (or random if not AI)
        if colorToPlay == AI_color:
            ActualPosition = Node(PARAM_Depth,[
                AI_Advantage,
                colorToPlay,
                None,
                None
            ])
            ActualPosition.clearChilds()

            _head = ActualPosition
            _color = colorToPlay

            # Reset minimax stats
            TEMP_calculatedScenarios = 0

            
            # generate Tree
            generateScoreTree(Analyzer,_head,_color,PARAM_Depth)
            #print('Tree done !')
            
            
            # search the best path
            bestMove = minimax(_head,_color,0,PARAM_Depth)
            #print('Best move found !')

            """
            if AI_color == 'black':
                # Select the best move for black (depth = 1)
                bestMove = None
                bestScore = float('-inf')
                for child in ActualPosition.childs():
                    childData = child.data()
                    if childData[3] == True:
                        bestMove = childData[2]
                        break
                    elif childData[3] == None:
                        if childData[0] > bestScore:
                            bestMove = childData[2]
                            bestScore = childData[0]
            else:
                # Select the best move for white (depth = 1)
                bestMove = None
                bestScore = float('inf')
                for child in ActualPosition.childs():
                    childData = child.data()
                    if childData[3] == True:
                        bestMove = childData[2]
                        break
                    elif childData[3] == None:
                        if childData[0] < bestScore:
                            bestMove = childData[2]
                            bestScore = childData[0]
            """
            
            Analyzer.move(bestMove)
            Analyzer.saveBoard(s)

        else:
            # Let user choose move
            if PARAM_randomAI_OP_Moves:
                # Select a random move
                next_move = random.choice(list(Analyzer.getLegalMoves()))
                Analyzer.move(next_move)
            else:
                legalsMoves = list(Analyzer.getLegalMoves())
                for i,move in enumerate(legalsMoves):
                    print(str(i)+' : '+str(move))
                wait = int(input())
                Analyzer.move(legalsMoves[wait])

            Analyzer.saveBoard(s)


        if colorToPlay == AI_color:
            colorToPlay = AI_OP_color
        else:
            colorToPlay = AI_color


        if PARAM_ConsoleBoard:
            Analyzer.drawBoard(s)
        if PARAM_ConsoleSteps:
            print('{}: {}'.format(s,AI_Advantage))

        if PARAM_ConsoleBoard or PARAM_ConsoleSteps:
            print('')


        s+=1

    return [MEMORY_AI_Advantages,MEMORY_Lichess_Advantages]


x = [i for i in range(PARAM_maxTurn)]

if PARAM_BigTest:
    i = 1
    endPoints = []
    while i <= PARAM_BigTest_count:
        tempRes = Simulation()[0]
        endPoint = tempRes[len(tempRes)-1]
        endPoints.append(endPoint)

        plt.plot(x, correctSize(tempRes,PARAM_maxTurn), color='black', alpha=0.2)
        if PARAM_ConsoleBigTest:
            print('{}/{}'.format(i,PARAM_BigTest_count))
        i += 1
    
    averageEndpoint = sum(endPoints) / len(endPoints)
    print(averageEndpoint)
    
    plt.plot(x, fillSize([averageEndpoint],PARAM_maxTurn), color='green', alpha=0.4)
    plt.plot(x, fillSize([0],PARAM_maxTurn), color='red', alpha=0.4)

else:
    plt.plot(x, correctSize(Simulation()[0],PARAM_maxTurn), color='red')



if PARAM_CompareToLichess:
    plt.plot(x, MEMORY_Lichess_Advantages, color='green')

plt.ylabel('AI Advantage per turn')
print(TEMP_calculatedScenarios)
plt.show()
