# benchvice

Programmatic interaction with VICE emulator

The motivating racket is to make a programmatic interface to Sargon II Chess
running on VIC-20 - the chess program I was never able to beat as a small child.
I have learned some chess since then but I've also acquired insufferable
standards for user interface design that Sargon II simply does not meet. Putting
a modern Chess front-end on Sargon II running in an emulator is the only path
forward. Plus, if it turns out my chess still does not enable me to beat it by
hand, perhaps my programming could enable me to beat it with a bot. 

Initial experiments with the VICE showed promise but there are bugs in VICE, in
my code or in my own brain when it comes to achieving fast interrogation of the
state of the VIC-20 memory and submitting moves to the game. Consulting the
assembly source code and spending the requisite hours in the VICE monitor has
revealed the memory locations for board and game state and I know how to
automate keyboard input to make moves. The problem is that communicating with
VICE over a socket seems to result in unpredictable hanging. More work and
renewed vigour is required.

`sargon.sh` is a bash script written for launching `xvic` from VICE with Sargon
II chess. The patched `.prg` from
[jamarju](https://github.com/jamarju/vic20-sargon-ii-chess) works for me but the
original `.crt` image reaches a CPU jam once the game starts. This version has
also been helpful for understanding how Sargon works.

The script interacts with Sargon II using the VICE remote monitor with the aim
of enabling integration of Sargon with other chess-playing infrastructure.

## Sargon Memory Locations

Screen memory is at `$1e00` which makes reading the board possible, given that
it is character mapped graphics and the `2x2` character chess pieces all have
a unique top left char. So the top left of the `2x2` characters for each square
betrays the piece on the square, including the colour. The board orientation is
fixed with white at the bottom.

## TODO

For Sargon

* [ ] investigate binary monitor protocol. The text commands appear to have
  changed a lot over time and parsing natural language output seems brittle.
  After some work, in fact it seems to be the opposite case.
  * [ ] try asynchronous socket implementation of `vice_connect.py`
* [ ] Q: do we need to set the keyboard buffer size when sending keys?
* [ ] read general game state from memory
  * [ ] computer is thinking?
  - [ ] initial title screen (hit `F1`)
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
* [x] take screenshot

## Alternatives to VICE

* <https://github.com/nippur72/vic20-emu>
* <https://github.com/rjanicek/vice.js>
* <https://github.com/abbruzze/kernal64> Scala
* <https://github.com/hotkeysoft/emulators>
* <https://github.com/gcasa/VIC20>
* <https://github.com/mrangryhumster/vic20_crude_emulator>
* <https://github.com/breqdev/noentiendo>
