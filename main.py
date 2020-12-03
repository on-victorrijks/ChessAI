import chess
import chess.svg
import random
import matplotlib.pyplot as plt

import theorical_position_advantage as ENGINE_ADV_POSITION


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
    "pieceValue": 1,
    "theorical_position": 0.05,
    "maxVictimValue": 0.2,
    "nbThreats": 0.2
}

class Analyzer:

    def __init__(self,AI_color):
    
        if AI_color == 'black':
            self.AI_color = True
        else:
            self.AI_color = False

        self.__board = chess.Board()

    def setFEN(self,fen):
        self.__board.set_fen(fen)

    def getFEN(self):
        return self.__board.fen()

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
                maximumVictimValue = max(victimsValues)

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

        if pieceType == "QUEEN":
            formulaResult -= pieceValue
                               

        return formulaResult


    def getBoardDetails(self):
        boardData = {
            'black': [],
            'white': []
        }

        legal_moves = self.getLegalMoves()
        legal_moves_starter = [m.uci()[0:2] for m in legal_moves]
        legal_moves_ender = [m.uci()[2:4] for m in legal_moves]

        for i in range(64):
            pieceType = self.__board.piece_type_at(i)
            pieceColor = self.__board.color_at(i)
            piecePosition = chess.square_name(i)

            if pieceColor != None:
                if pieceColor:
                    pieceClass = 'black'
                else:
                    pieceClass = 'white'
                    
                possibleVictims = [p for p in self.__board.attacks(i) if not self.__board.color_at(p) and chess.square_name(p) in legal_moves_ender ]
                possibleAttacker = [a for a in self.__board.attackers(not self.AI_color,i) if chess.square_name(a) in legal_moves_starter ]


                boardData[pieceClass].append({
                    'type': pieceTypes[pieceType-1],
                    'position': piecePosition,
                    'attacks': possibleVictims,
                    'attackers': possibleAttacker
                })
        
        return boardData


MEMORY_AI_Advantages = []
AI_color = 'black'
AI_OP_color = 'white'
Analyzer = Analyzer(AI_color)
s = 0
nb_moves = 200

toMove = AI_color

# Test FEN
Analyzer.setFEN('2r4r/1k1p3b/7p/6p1/q3P3/P3KR2/1P5B/1Q1R4 w - - 0 1')

while not Analyzer.isCheckmate() and s < nb_moves:
    

    allMoves = Analyzer.getBoardDetails()
    # AI moves
    AI_Moves = allMoves[AI_color]
    AI_score = 0
    for moveIndex,moveData in enumerate(AI_Moves):
        AI_score += (Analyzer.generateMoveScore(moveData,AI_color))

    # AI-Opposite moves
    AI_OP_Moves = allMoves[AI_OP_color]
    AI_OP_score = 0
    for moveIndex,moveData in enumerate(AI_OP_Moves):
        AI_OP_score += (Analyzer.generateMoveScore(moveData,AI_OP_color))
    
    # AI advantage
    AI_Advantage = AI_score - AI_OP_score

    # big gain
    if len(MEMORY_AI_Advantages) > 0:
        AI_Advantage_last = MEMORY_AI_Advantages[(len(MEMORY_AI_Advantages)-1)]
    else:
        AI_Advantage_last = 1
    
    if AI_Advantage_last == 0:
        AI_Advantage_last = 0.01



    if AI_Advantage < 0:
        pass
        #print('AI OP is winning',(AI_Advantage))
    elif AI_Advantage == 0:
        pass
        #print('No winner')
    else:
        pass
        #print('AI is winning',(AI_Advantage))

    print(s,Analyzer.getFEN())

    # Save board as a file
    Analyzer.saveBoard(s)

    # RANDOM MOVE
    next_move = random.choice(list(Analyzer.getLegalMoves()))

    
    Analyzer.move(next_move)

    if toMove == AI_color:
        toMove = AI_OP_color
        MEMORY_AI_Advantages.append(AI_Advantage)
    else:
        toMove = AI_color
        MEMORY_AI_Advantages.append(AI_Advantage)
    
    s+=1

def getAverageScore2turn(raw):

    MEMORY_Average_Advantages = []

    for i,v in enumerate(raw):

        if i%2 == 0:
            lastElm = raw[i-1]
            avg = (lastElm + v) /2
            MEMORY_Average_Advantages.append(avg)

    return MEMORY_Average_Advantages

plt.plot(MEMORY_AI_Advantages)
plt.ylabel('AI Advantage per turn')
plt.show()

plt.plot(getAverageScore2turn(MEMORY_AI_Advantages))
plt.ylabel('AI Advantage per turn (avg)')
plt.show()

