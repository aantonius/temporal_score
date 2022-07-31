# temporal_score
## An experiment in active musical notation

This is a very-much work in process experiment in the possiblities created by introducing an intrinsic notion of time into musical scoring, using the neoscore library.
The code in its current form reflects both philosophical uncertainty in the final form of this experiment, but also technical uncertainty in how to achieve this.

## Running
The file `typesetter.py` should run if there is a working install of neoscore and its dependencies in the python environment.

```
python typesetter.py
```

will read the definition of the score in the file `score.txt` and create a file `score.html` that displays the animated score.  It does not open a qt window displaying the score as in a standard usage of neoscore.

### Note
The code currently generates an svg for each frame, diffs them, and outputs javascript to recreate the frames.  While this works, it is very slow and the output size is large.  A better solution would be to work out the sequence for each temporal object, and copy the timing logic in the javascript code.  This would massively reduce both running time and output size.

## score.txt
This file, currently a hardcoded name, contains the represention of the score in a text format.
Each line is either a single word, which represents some non-note element to be inserted (for instance a repeat indicator) or two tab-spaced groups of notes.  In each group the notes are seperated by spaces
The notation used for notes is a modification of that used by neoscore, itself a modification of Lilypond's.  Rather than write `f#'`, we write `f'#`.
The reason for this modification is that we wish to allow elements to have a temporal indication applied to them, for instance
```
f'(10 3 17)#
```
indicates that the f# is active for 10 frames out of every 17, from the 3 frame.  That is to say taking the frame count modulo 17, the note is off for frames 0,1,2, then on for 3 to 12, then off again.
We may also wish instead to apply timing to an accidental, for example
```
f'#(10 3 17)
```
This would create ambiguity if we stuck with the original ordering.


## The idea
The 20th century saw a great amount of experimentation in musical notation, however one could argue that nearly all of these experiments could be seen as placing us on different points on the same axis, either increasing the precision of the notation, for example with micro-tonal notation to allow the composer to more accurately define the sound desired; or decreasing the precision of what exact notes or timings are to be played, as many examples of graphical notation do, allowing the player more freedom to work with the overall "shape" of the music that the composer wanted to convey.


The possiblity of displaying scores on a digital device opens up interesting new possibilites in notation, specifically we can build notations that are not stuck to choosing different points on the axis of precision.


A digital score allows us to define a score that can change during the playing of the piece.  If it did not change, then it does not offer a possibility beyond that of a printed score.


The score could either change based on internal or external inputs.  I have chosen here to focus entirely upon internal inputs, and specifically that of time.  To allow external inputs raising some interesting questions, as these inputs must be taken, and processed, the question arrises as to whether the device is displaying a score, or is a one-off specialized musical instrument in and of itself.  There are certainly interesting possibilities for creation, but one is in danger of abandonning the score as score.  By this, I mean that the utility and the longevity of the musical score as concept is due to the fact that it can be reproduced, transmitted and still function to reproduce, to a greater or lesser extent, the sound and effect desired by the composer.
By tying the score to closely to a certain mechanical setup, this no longer holds.
So to create a score that functions as a score, I have decided here that the output should be an html file, something which is widely reproducible by a large variety of devices, and to restrict myself to inputs that can be achieved with that, with no other backend.


This has lead to the idea of using time as a fundamental component of the notation.  We simultaneously remove the durational component of the notational system, while introducing a strict logic of which notes are playable at a given time.  This means that the player can choose the speed and tempo as they progress through the piece, but these choices will interact with the temporal logic given by the composer, meaning that we will get potentially very different results based upon the players choices, although still remaining within the framework chosen by the composer.


Similarly to how a side-scrolling video game works, the composer chooses the overall feel and possible interactions of the level, but the player has control as to how the proceed and interact with this construction.  A dialogue is create between the two as they explore the possiblities of the construct, with different motifs and tonal combinations being possible, but perhaps in such a way that one excludes the other.

## Playing the output

As mentioned above, there is no durational instruction in this score.  Each note is rendered as a crotchet.  Notes with timing information are either black if they are currently playable, or greyed out if not.  A greyed out note will darken slightly just before it triggers to black, to give some warning to the player.  Other notational elements such as repeat lines, coda, and so on can also have timing information attached to them, and be either off (light-grey), or on (black).  In all cases, a player should play a note, or take a direction if and only if it is the immediate next item of notation, and is on.  By controlling their progress through the piece, the player can make choices as to the choice they will end up having to make.



