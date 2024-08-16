# benchvice

Programmatic interaction with VICE emulator

`sargon.sh` is a bash script written for launching `xvic` from VICE with Sargon II chess. The patched `.prg` from [jamarju](https://github.com/jamarju/vic20-sargon-ii-chess) works for me but the original `.crt` image reaches a CPU jam once the game starts. This version has also been helpful for understanding how Sargon works. 

The script interacts with Sargon II using the VICE remote montitor with the aim of enabling integration of Sargon with other chess-playing infrastructure.

## Sargon Memory Locations

Screen memory is at `$1e00` which makes reading the board possible, given that it is character mapped graphics and the 2x2 character chess pieces all have a unique top left char. So the top left of the 2x2 characters for each square betrays the piece on the square, including the colour. The board orientation is fixed with white at the bottom.



## TODO

For Sargon

* [ ] investigate binary monitor protocol. The text commands appear to have changed a lot over time
and parsing natural language output seems brittle
  * [ ] try asynchronous socket implementation of `vice_connect.py`
* [ ] Q: do we need to set the keyboard buffer size when sending keys? 
* [ ] read general game state from memory
    * [ ] computer is thinking?
    * [ ] initial title screen (hit F1)
    * [ ] Game or Setup prompt
    * [ ] Game: 
      * [x] Human colour
      * [x] White or Black prompt
      * [ ] AI level 0-6
    * [ ] Setup: 
        * to specify a board state from which to play
    * [ ] level of difficulty
    * [x] pieces at each square on board
    * [ ] latest move
    * [ ] move history (whether a piece has moved etc.)
* [ ] read vice state
    * [ ] prg is loading from disk/tape
    * [ ] warp mode? 
* [x] screenshot


## Alternatives to VICE

* https://github.com/nippur72/vic20-emu
* https://github.com/rjanicek/vice.js
* https://github.com/abbruzze/kernal64
* https://github.com/hotkeysoft/emulators
* https://github.com/gcasa/VIC20
* https://github.com/mrangryhumster/vic20_crude_emulator
* https://github.com/breqdev/noentiendo

