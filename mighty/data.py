from dataclasses import dataclass
from enum import Flag, auto

class WordType(Flag):
    NOUN = auto()
    VERB = auto()
    ADJECTIVE = auto()
    ADVERB = auto()

# PHONETICS OH GOD NO
@dataclass
class Word:
    text: str
    type: WordType
    alliteration: str
    assonance: tuple[str] # not a set cause maybe it appears mutliple time for really good words? (does that matter)
    rhyme: str # Should this actually be a set of phonemes so you can rhyme smartly (ahhhhh)
    # partial_rhyme: set[str] # I'm not even sure if this should be a thing
    length: int # sylibals

@dataclass
class Blank:
    type: WordType # Valid Word types to go here
    alliteration: set[str] # viable alliteration that score
    assonance: set[str] # viable assoance that score
    rhyme: set[str] # viable rhymes that score
    length: int # ideal length of the word that score (should maybe be a set aswell)

class FillIn:

    def __init__(self, *words: str | Blank):
        self.words = []
        self.blanks = []
        for word in words:
            if isinstance(word, str):
                self.words.append(word)
            elif isinstance(word, Blank):
                self.words.append(None)
                self.blanks.append(word)

class Card:
    
    def __init__(self, fill: FillIn, blanks: list[Word]):
        self.fill = fill
        self.blanks = blanks

        c = blanks[:]
        self.text = ' '.join(word or f'[{c.pop(0).text}]' for word in self.fill.words)

    fill_in: FillIn
    blanks: list[Word]

WORDS = (
    Word('apple', WordType.NOUN, 'a', (), 'le', 2),
    Word('winner', WordType.NOUN, 'w', ('i'), 'ner', 2),
    Word('dinner', WordType.NOUN, 'd', ('i'), 'ner', 2),
    Word('thinner', WordType.NOUN | WordType.ADJECTIVE, 'th', ('i'), 'ner', 2),
    Word('corner', WordType.NOUN | WordType.VERB, 'c', ('o'), 'ner', 2),
    Word('brag', WordType.VERB, 'b', (), 'ag', 1),
    Word('drag', WordType.VERB | WordType.NOUN, 'd', (), 'ag', 1),
)

# So fill ins are actually currently written to be able to take any number of blanks
# For simplicity scoring and figuring out the words I haven't done that lmao
# Id actually like the whole FillIn words and Blanks. That way we could score smart FillIn usage not just the blanks
# Like if you made every line start with the same sound that works for alliteration, but would be really hard to score rn
# Plus repeating similar phrases should be bad right?
# For the ideal length thats from a this-phrase-only-perspective. Cause having every word have the same length is way better
FILLINS = (
    # Found our first problem ;-; `like` and `dinner` aren't the same `i` sound -.-
    FillIn("you're", "slow", "like", "a", Blank(WordType.NOUN, set(), {'i', 'o'}, set(), 1)), 
    FillIn("I", "wouldn't", "Be", Blank(WordType.VERB, set(), set(), set(), 2)),
    # Id actually make this two blanks. Swap out `corpse` but for now...
    FillIn("or", "your", "corpse", "I'll", "Be", Blank(WordType.VERB, set(), {'o'}, set(), 2)),
    FillIn("you", "look", "like", "a", Blank(WordType.NOUN, {'l'}, {'o'}, set(), 1))
)