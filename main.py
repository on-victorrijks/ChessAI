import chess
import chess.svg
import random
import matplotlib.pyplot as plt
from minimax import *
import functools
import time



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
    "pieceValue": 3,
    "theorical_position": 0.5,
    "maxVictimValue": 1.2,
    "nbThreats": 0.7,
    "case_protected": 0.1
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
                res[0] = 2
                res[1] = 2
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

def getScoreFromSimulatedBoard_for(Moves):
    score = 0
    for moveIndex,moveData in enumerate(Moves):
        score += (Analyzer.generateMoveScore(moveData,AI_color))
    return score

def getScoreFromSimulatedBoard(Analyzer,colorToPlay,AI_color,AI_OP_color):
    # Get board details
    moves = Analyzer.getBoardDetails()

    # Reset the playing color
    Analyzer.setPlayingColor(colorToPlay)

    # AI moves
    AI_Moves = moves[AI_color]
    AI_score = getScoreFromSimulatedBoard_for(AI_Moves)

    # AI-Opposite moves
    AI_OP_Moves = moves[AI_OP_color]
    AI_OP_score = getScoreFromSimulatedBoard_for(AI_OP_Moves)

    
    # AI advantage (/!\)
    AI_Advantage = AI_OP_score - AI_score

    return AI_Advantage


def generateScoreTree(Analyzer,_head,_color,_depth,debug=False):
    global TEMP_calculatedScenarios

    DebugState = False

    if _depth > 0:

        # Get the correct color

        Analyzer.setPlayingColor(_color)
        legalsMoves = list(Analyzer.getLegalMoves())
        simulatedColor = oppositeColor(_color)

        for move in legalsMoves:

            # Simulate move
            Analyzer.move(move)
            # Results
            res = Analyzer.getResult()
            specialTreatement = None
            if res[AI_color] == 1.0:
                specialTreatement = True
            elif res[AI_color] == 2.0:
                # never surrender
                specialTreatement = False
            elif res[AI_color] == 0.0:
                specialTreatement = False                


            # Getting the score
            score = getScoreFromSimulatedBoard(Analyzer,simulatedColor,AI_color,AI_OP_color)
            TEMP_calculatedScenarios += 1
            if TEMP_calculatedScenarios % PARAM_ConsoleCalculationsStack == 0 and PARAM_ConsoleCalculations:
                print('{} simulations...'.format(TEMP_calculatedScenarios))

            # Create node
            child = Sim(score,move,specialTreatement)
            
            if PARAM_Fast and (PARAM_Depth-_depth) < 2:
                if score > (_head.getData()-PARAM_FastThreshold):
                    generateScoreTree(Analyzer,child,simulatedColor,(_depth-1),DebugState)
            else:
                generateScoreTree(Analyzer,child,simulatedColor,(_depth-1),DebugState)

            Analyzer.back()

            _head.addChild(child)

def minimax(_head,_color,_depth,maxDepth,alert=False):    

    SpecialTreatement = _head.getSpecial()

    if _depth == maxDepth:
        # bottom elements

        # Detect gameover
        if SpecialTreatement == True:
            return ((maxDepth+1)-_depth)*1000
        elif SpecialTreatement == False:
            return float('-inf')
        else:
            return _head.getData()
    else:

        # Detect gameover
        if SpecialTreatement == True:
            return ((maxDepth+1)-_depth)*1000
        elif SpecialTreatement == False:
            return float('-inf')
        else:
            
            _oppositeColor = oppositeColor(_color)
            _depthPO = _depth+1
            advantages = []
            childs = _head.getChilds()

            for child in childs:
                temp_minimax = minimax(child,_oppositeColor,_depthPO,maxDepth) 
                advantages.append(temp_minimax)

            # /!\ To test
            if len(advantages) == 0:
                return float('inf')

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

def Simulation():

    global AI_color
    global AI_OP_color

    MEMORY_AI_Advantages = []
    MEMORY_Lichess_Advantages = []

    colorToPlay = PARAM_ColorToPlay

    s = 1
    nb_moves = PARAM_maxTurn


    # Start the lichess comparator
    if PARAM_CompareToLichess:
        instance = LichessComparator(AI_color,True)
        isConnected = instance.connectToLichess()
        print('Lichess Comparator connection: {}'.format(isConnected))

    # Reset Board
    Analyzer.reset()

    # Test FEN
    #Analyzer.setFEN('1KR1Q2R/1B3PBP/P7/2PPN3/8/1pPpp2p/p1p2qb1/r1bk2nr w kq - 0 14')


    # First board
    Analyzer.saveBoard(0)


    while not Analyzer.isGameOver() and s <= nb_moves:

        
        # Actual board configuration score generator
        AI_Advantage = getScoreFromSimulatedBoard(Analyzer,colorToPlay,AI_color,AI_OP_color)

        ## Graph data collector
        if Initial_AI_color == 'black':
            if AI_color == 'black':
                MEMORY_AI_Advantages.append(-AI_Advantage)
            else:
                MEMORY_AI_Advantages.append(AI_Advantage)
        else:
            if AI_color == 'black':
                MEMORY_AI_Advantages.append(AI_Advantage)
            else:
                MEMORY_AI_Advantages.append(-AI_Advantage)

        # Lichess score comparator
        actualFEN = Analyzer.getFEN()
        if PARAM_CompareToLichess:
            lichessScore = instance.getScore(actualFEN)
            MEMORY_Lichess_Advantages.append(lichessScore)


        # Use minimax to select a move (or random if not AI)
        if colorToPlay == AI_color:
            ActualPosition = Sim(AI_Advantage,None,None)
            ActualPosition.clearChilds()

            _head = ActualPosition
            _color = colorToPlay

            # Reset minimax stats
            TEMP_calculatedScenarios = 0

            
            # generate Tree
            if PARAM_ConsoleSteps:
                time_tree = time.time()
            
            if PARAM_PlayAgainstHimself and PARAM_PAH_DiffDepth:
                if AI_color != Initial_AI_color:
                    generateScoreTree(Analyzer,_head,_color,PARAM_Depth_OP)
                else:
                    generateScoreTree(Analyzer,_head,_color,PARAM_Depth)
            else:
                generateScoreTree(Analyzer,_head,_color,PARAM_Depth)

            # order first line of the tree
            _head.orderChilds()
            if PARAM_ConsoleSteps:
                print('Tree generated: {}s'.format((time.time() - time_tree)))

            # Log tree (advanced debugging)
            if PARAM_LogTree:
                temp = _head.showTree(0)
                f = open("tree.debug", "a")
                f.write(temp)
                f.close()
                i = str(input('ENTER TO LOG ANOTHER TREE'))

            # search the best path
            if PARAM_ConsoleSteps:
                time_pathMoveFinder = time.time()
            bestMove = minimax(_head,_color,0,PARAM_Depth)
            if PARAM_ConsoleSteps:
                print('Move found: {}s'.format((time.time() - time_pathMoveFinder)))

            
            if PARAM_ConsoleMoves:
                print(bestMove)

            Analyzer.move(bestMove)
            Analyzer.saveBoard(s)

            if PARAM_PlayAgainstHimself:
                AI_OP_color = AI_color
                AI_color = oppositeColor(AI_color)
    
        else:
            
            if PARAM_randomAI_OP_Moves:
                # Select a random move
                next_move = random.choice(list(Analyzer.getLegalMoves()))
                Analyzer.move(next_move)
            else:
                # Let user choose move
                legalsMoves = list(Analyzer.getLegalMoves())

                for i,move in enumerate(legalsMoves):
                    print(str(i)+' : '+str(move))

                goodInp = False
                while not goodInp:
                    try:
                        wait = int(input())
                        if wait <= (len(legalsMoves)-1):
                            userMove = legalsMoves[wait]
                            goodInp = True
                    except:
                        goodInp = False
                    
                Analyzer.move(userMove)

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
            #print('')
            pass


        s+=1

    return [MEMORY_AI_Advantages,MEMORY_Lichess_Advantages]




if __name__ == '__main__':

    MEMORY_AI_Advantages_BIGTEST = []

    Initial_AI_color = 'black'

    AI_color = Initial_AI_color
    AI_OP_color = oppositeColor(AI_color)

    Analyzer = Analyzer(AI_color)

    MEMORY_AIAdvantage = 0

    PARAM_CompareToLichess = False
    PARAM_ConsoleSteps = True
    PARAM_ConsoleBoard = False
    PARAM_ConsoleBigTest = False
    PARAM_ConsoleCalculations = True
    PARAM_ConsoleCalculationsStack = 25000
    PARAM_ConsoleMoves = False
    PARAM_BigTest = False
    PARAM_BigTest_count = 100
    PARAM_LogTree = False
    PARAM_randomAI_OP_Moves = False
    PARAM_maxTurn = 100

    PARAM_ColorToPlay = 'white'

    PARAM_PAH_DiffDepth = False
    PARAM_Depth = 2
    PARAM_Depth_OP = 2

    PARAM_Fast = False
    PARAM_FastThreshold = 2


    PARAM_showAdv = True
    PARAM_PlayAgainstHimself = True
    TEMP_calculatedScenarios = 0
    

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

    plt.ylabel('AI Advantage per turn ('+Initial_AI_color+')')
    print(TEMP_calculatedScenarios)
    if PARAM_showAdv:
        plt.show()
