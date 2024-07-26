# benchvice

Programmatic interaction with VICE emulator

`sargon.sh` is a bash script written for launching `xvic` from VICE with Sargon II chess. The patched `.prg` from [jamarju](https://github.com/jamarju/vic20-sargon-ii-chess) works for me but the original `.crt` image reaches a CPU jam once the game starts. This version has also been helpful for understanding how Sargon works. 

The script interacts with Sargon II using the VICE remote montitor with the aim of enabling integration of Sargon with other chess-playing infrastructure.

## TODO

For Sargon

* [ ] investigate binary monitor protocol. The text commands appear to have changed a lot over time and parsing natural language output seems brittle
* [ ] read general game state from memory
    * [ ] initial title screen (hit F1)
    * [ ] Game or Setup prompt
    * [ ] Game: 
        * [ ] White or Black prompt
        * [ ] AI level 0-6
    * [ ] Setup: 
        * to specify a board state from which to play
    * [ ] computer is thinking?
    * [ ] level of difficulty
    * [ ] board state (pieces on board, captured, have moved etc.)
    * [ ] latest move
    * [ ] move history
* [ ] read vice state
    * [ ] prg is loading from disk/tape
    * [ ] warp mode? 
* [ ] screenshot

