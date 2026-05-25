from random import choice
from time import sleep
import sys
import os

# Import speak from backend
try:
    from backend.TextToSpeech import speak
except ImportError:
    # Handle path when running directly or from main
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.TextToSpeech import speak

def game():
    print("********GIVE STAR ONLY IF YOU LIKE************")
    
    def Welcome():
        msg = 'Welcome to tic-tac-toe game'
        print(f'   ****{msg}****')
        speak(msg)
        sleep(1)
        print('\nComputer will decide who will play first')
        print('\nIf you need Hint in the middle of game press any of this [Hint,hint,H,h]')
        sleep(1)
        print('''      ******* Format of Game ******
              |    |         1 | 2 | 3
           - - - - - -      - - - - - - 
              |    |         4 | 5 | 6
           - - - - - -      - - - - - - 
              |    |         7 | 8 | 9
                                           ''')

    def DrawBoard(board,NeedSleep=True):
        if NeedSleep:
            sleep(1)
            print()
            print('             '+board[1]+'  |  '+board[2]+'  |  '+board[3])
            print('             - - - - - - - ')
            print('             '+board[4]+'  |  '+board[5]+'  |  '+board[6])
            print('             - - - - - - - ')
            print('             '+board[7]+'  |  '+board[8]+'  |  '+board[9])
        print()

    def InputPlayerLetter():
        letter=''
        while not(letter == 'X' or letter == 'O'):
            msg = 'Do you want to be X or O?'
            print(msg)
            speak(msg)
            letter = input().upper()
        return ['X','O'] if letter == 'X' else ['O','X']

    def WhoFirst():
        return choice(['computer','player'])
        
    def PlayAgain():
        msg = 'Do you want to Play Again? Yes or No?'
        print(f'\n{msg}')
        speak(msg)
        return input().lower().startswith('y')

    def MakeMove(board,letter,move):
        board[move] = letter

    def IsWinner(board,letter):
        return ( (board[7] == letter and board[8] == letter and board[9] == letter ) or
                 (board[4] == letter and board[5] == letter and board[6] == letter ) or
                 (board[1] == letter and board[2] == letter and board[3] == letter ) or
                 (board[1] == letter and board[4] == letter and board[7] == letter ) or
                 (board[2] == letter and board[5] == letter and board[8] == letter ) or
                 (board[3] == letter and board[6] == letter and board[9] == letter ) or
                 (board[1] == letter and board[5] == letter and board[9] == letter ) or
                 (board[3] == letter and board[5] == letter and board[7] == letter )  )

    def GetBoardCopy(board):
        return list(board)
    
    def IsSpaceFree(board,move):
        return board[move] == ' '

    def GetPlayerMove(board):
        move = ''
        hint_input = ['Hint','hint','H','h']
        while move not in '1 2 3 4 5 6 7 8 9'.split() or not IsSpaceFree(board,int(move)):
            print('Enter your move (1 - 9)')
            move = input()
            if move in hint_input:
                return move
        return int(move)

    def ChooseRandomFromList(board,MoveList):
        PossibleMoves = [i for i in MoveList if IsSpaceFree(board,i)]
        return choice(PossibleMoves) if PossibleMoves else None

    def GetComputerMove(board,ComputerLetter):
        PlayerLetter = 'O' if ComputerLetter == 'X' else 'X'
        for i in range(1,10):
            copy = GetBoardCopy(board)
            if IsSpaceFree(copy,i):
                MakeMove(copy,ComputerLetter,i)
                if IsWinner(copy,ComputerLetter): return i
        for i in range(1,10):
            copy = GetBoardCopy(board)
            if IsSpaceFree(copy,i):
                MakeMove(copy,PlayerLetter,i)
                if IsWinner(copy,PlayerLetter): return i
        move = ChooseRandomFromList(board,[1,3,7,9])
        if move: return move
        if IsSpaceFree(board,5): return 5
        return ChooseRandomFromList(board,[2,4,6,8])

    def IsBoardFull(board):
        return all(not IsSpaceFree(board, i) for i in range(1, 10))
            
    def FinalBoard(board,NeedSleep=True):
        print('            |-------------|')
        DrawBoard(board,NeedSleep)
        print('            |-------------|')

    Welcome()
    while True:
        TheBoard = [' '] * 10
        PlayerLetter,ComputerLetter = InputPlayerLetter()
        turn = WhoFirst()
        msg = f'The {turn} will go first'
        print(msg)
        speak(msg)
    
        Playing = True
        while Playing:
            if turn == 'player':
                print(f"  Turn => {turn}") 
                move = GetPlayerMove(TheBoard)
                if isinstance(move, str):
                    hint = GetComputerMove(TheBoard, PlayerLetter)
                    msg = f'Hint: placing at {hint} is better'
                    print(msg)
                    speak(msg)
                    continue
                  
                MakeMove(TheBoard,PlayerLetter,move)
                if IsWinner(TheBoard,PlayerLetter):
                    FinalBoard(TheBoard)
                    msg = 'Congratulations! You have won the game!'
                    print(msg)
                    speak(msg)
                    Playing = False
                elif IsBoardFull(TheBoard):
                    FinalBoard(TheBoard)
                    msg = 'The game is a tie!'
                    print(msg)
                    speak(msg)
                    Playing = False
                else:
                    DrawBoard(TheBoard)
                    turn = 'computer'
            else:
                print(f"  Turn => {turn}")
                move = GetComputerMove(TheBoard,ComputerLetter)
                MakeMove(TheBoard,ComputerLetter,move)
                if IsWinner(TheBoard,ComputerLetter):
                    FinalBoard(TheBoard)
                    msg = 'Computer won. Better luck next time!'
                    print(msg)
                    speak(msg)
                    Playing = False
                elif IsBoardFull(TheBoard):
                    FinalBoard(TheBoard)
                    msg = 'The game is a tie!'
                    print(msg)
                    speak(msg)
                    Playing = False
                else:
                    DrawBoard(TheBoard)
                    turn = 'player'

        if not PlayAgain():
            break
