from technicals import *

POSITION_BONUS = {
    'eligibles':[
        'PAWN',
        'BISHOP',
    ],
    'PAWN': [
        'd4',
        'd5',
        'e4',
        'e5'
    ],   
}



def raw(position, pieceType, pieceColor):
    advantage = 0

    # How close is it to the center
    positionLst = list(position)
    position_horizontal = letterPosToIntPos(positionLst[0])
    position_vertical = int(positionLst[1])

    diffCenter_horizontal = abs(4.5 - position_horizontal)
    diffCenter_vertical = abs(4.5 - position_vertical)

    advantage_center = 1/diffCenter_horizontal + 1/diffCenter_vertical
    advantage += advantage_center

    # Position BONUS

    if pieceType in POSITION_BONUS['eligibles']:

        if pieceType == 'PAWN':
            if position in POSITION_BONUS['PAWN']:
                advantage += 2
        
        elif pieceType == 'BISHOP':
            
            # is it in the king side ?

            if position_horizontal < 4.5:
                advantage += 2


    return advantage