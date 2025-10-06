Operations
For graphical interface:
    Run gui.py file through your prefered Python launcher
    To run through the command line, run the following command
        'python <file-path>/main.py'

    User controls:
        On Launch:
          Use 'Rows', 'Cols', and 'Bombs' fields to set board size and number of mines
            NOTE: fields do not show indication of being selected, but do function
          AI button toggles AI system between OFF and ON
            Reveals additional controls for AI system if set to ON
            INTERACTIVE allows for competitive play against the computer, with turns traded between the player and computer
            AUTOMATIC allows the computer to play by itself
            If neither option is chosen, the AI system operates in OFF mode
            EASY, MEDIUM, and HARD allow the player to chose between the levels of AI difficulty
            Start Game begins the game with the current settings            
        Board cells:
            Left click: reveals cell, whether cell contains a mine or not
            Right click: flags or unflags cell
          Game Over:
            On victory or success, ending message is displayed with controls for Play Again and Quit
            Play Again resets the game board and starts a new game, with the same settings
            Quit closes the program

Environmental requirements
Python version: Python3
Modules:
    random
    pygame
    os
    time
