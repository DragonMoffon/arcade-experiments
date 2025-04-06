from typing import Literal
from random import shuffle
from enum import IntEnum, StrEnum

class Suit(IntEnum):
    CLUB = 0
    DIAMOND = 1
    HEART = 2
    SPADE = 3

class Commands(StrEnum):
    FIGHT = "fight"
    FLEE = "flee"
    CONSUME = "consume"
    EQUIP = "equip"
    SWAP = "swap"
    USE = "use"

class bcolors:
    END = '\033[0m'
    HEALTH = '\033[31m'
    WEAPON = '\033[93m'
    MONSTER = '\033[92m'
    COMMAND = '\033[94m'
    CLUB = '\033[38;2;0;138;255m'
    DIAMOND = '\033[38;2;255;106;0m'
    HEART = '\033[38;2;255;0;0m'
    SPADE = '\033[38;2;0;0;0m'


CLUB_OPTIONS = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
DIAMOND_OPTIONS = 2, 3, 4, 5, 6, 7, 8, 9, 10
HEART_OPTIONS = 2, 3, 4, 5, 6, 7, 8, 9, 10
SPADE_OPTIONS = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14

SUIT_OPTIONS = CLUB_OPTIONS, DIAMOND_OPTIONS, HEART_OPTIONS, SPADE_OPTIONS

CARD_NAMES = "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"
SUIT_NAMES = "♣", "♦", "♥", "♠" 
SUIT_COLORS = bcolors.CLUB, bcolors.DIAMOND, bcolors.HEART, bcolors.SPADE

def get_card_name(suit: Suit, value: int):
    return f"{CARD_NAMES[value-2]} of {SUIT_NAMES[suit]}"

class Card:

    def __init__(self, suit: Suit, value: int):
        assert value in SUIT_OPTIONS[suit], f"The {SUIT_NAMES[suit]} suit cannot have a value of {value} {"" if not 11 <= value <= 14 else f"({CARD_NAMES[value-2]})"}"
        self.suit: Suit = suit
        self.value: int = value

    def __str__(self):
        return f"{SUIT_COLORS[self.suit]}{get_card_name(self.suit, self.value)}{bcolors.END}"
    
    def __repr__(self):
        return self.__str__()

class ScoundrelGame:

    def __init__(self) -> None:
        self._player_health: int = 20
        self._player_weapon: int | None = None
        self._lowest_defeated_moster: int | None = None
        self._has_fled: bool = False
        self._dungeon: list[Card] = []
        self._room: list[Card] = []
        self._discard: list[Card] = []

    def setup(self):
        self._player_health = 20
        self._player_weapon = None
        self._lowest_defeated_moster = None

        self._dungeon = [ Card(Suit(suit), value) for suit in range(4) for value in SUIT_OPTIONS[suit]]
        shuffle(self._dungeon)
        while len(self._room) < 4:
            self._room.append(self._dungeon.pop(0))

    @property
    def health(self) -> int:
        return self._player_health
    
    @property
    def weapon(self) -> int | None:
        return self._player_weapon
    
    @property
    def defeated_moster(self) -> int | None:
        return self._lowest_defeated_moster
    
    @property
    def can_flee(self) -> bool:
        return len(self._room) >= 4 and not self._has_fled

    def peek_card(self, idx: Literal[0, 1, 2, 3]) -> Card | None:
        if idx >= len(self._room):
            return None
        return self._room[idx]
    
    def get_card(self, idx: Literal[0, 1, 2, 3]) -> Card | None:
        if idx >= len(self._room):
            return None
        card = self._room.pop(idx)

        if len(self._room) <= 1:
            self._has_fled = False
            while len(self._room) < 4 and self._dungeon:
                self._room.append(self._dungeon.pop(0))

        return card
    
    def swap_cards(self, idx_a: Literal[0, 1, 2, 3], idx_b: Literal[0, 1, 2, 3]):
        if idx_a >= len(self._room) or idx_b >= len(self._room):
            raise KeyError(f"The room only has {len(self._room)} card in it and cannot swap {idx_a}<->{idx_b}")
        
        if idx_a == idx_b:
            return
        
        self._room[idx_a], self._room[idx_b] = self._room[idx_b], self._room[idx_a]

    def fight_card(self, card: Card, with_weapon: bool = False):
        if card.suit != Suit.CLUB and card.suit != Suit.SPADE:
            raise ValueError(f"{card} cannot be fought")
        
        with_weapon = with_weapon and self._player_weapon is not None and card.value < (self._lowest_defeated_moster or 20)
        diff = max(0, card.value - (self._player_weapon if with_weapon else 0))
        self._player_health = max(0, self._player_health - diff)
        if with_weapon:
            self._lowest_defeated_moster = card.value
        self.discard_card(card)

    def equip_card(self, card: Card):
        if card.suit != Suit.DIAMOND:
            raise ValueError(f"{card} cannot be equiped")
        
        self._player_weapon = card.value
        self._lowest_defeated_moster = None
        self.discard_card(card)

    def consume_card(self, card: Card):
        if card.suit != Suit.HEART:
            raise ValueError(f"{card} cannot be consumed")
        
        self._player_health = min(20, self._player_health + card.value)
        self.discard_card(card)

    def flee(self) -> bool:
        if len(self._room) < 4 or self._has_fled:
            return False
        shuffle(self._room)
        self._dungeon.extend(self._room)
        self._room = []
        while len(self._room) < 4 and self._dungeon:
            self._room.append(self._dungeon.pop(0))
        self._has_fled = True

    def discard_card(self, card: Card):
        pass

def process_command(cmd: str, game: ScoundrelGame):
    command, *args = cmd.lower().split(' ')
    idx = 0
    try:
        idx = int(command)
    except ValueError:
        if command != Commands.FLEE:
            idx = int(args[0])
    else:
        card = game.peek_card(idx)
        if card is None:
            raise KeyError(f"Invalid idx {idx}")
        
        if card.suit == Suit.CLUB or card.suit == Suit.SPADE:
            command = Commands.FIGHT
        else:
            command = Commands.USE

    match command:
        case Commands.FIGHT:
            with_weapon = 'weapon' in args or 'y' in args or 'yes' in args
            card = game.get_card(idx)
            game.fight_card(card, with_weapon)
        case Commands.CONSUME:
            card = game.get_card(idx)
            game.consume_card(card)
        case Commands.EQUIP:
            card = game.get_card(idx)
            game.co
        case Commands.SWAP:
            idx_b = int(args[1])
            game.swap_cards(idx, idx_b)
        case Commands.USE:
            card = game.get_card(idx)
            if card.suit == Suit.DIAMOND:
                game.equip_card(card)
            else:
                game.consume_card(card)
        case Commands.FLEE:
            game.flee()
    
game = ScoundrelGame()
game.setup()
while True:
    print(f"room: {game._room}, {bcolors.HEALTH}hp: {game.health}{bcolors.END}, {bcolors.WEAPON}wp: {game.weapon}{bcolors.END}, {bcolors.MONSTER}mo: {game.defeated_moster}{bcolors.END}, remaining: {len(game._dungeon)}")
    cmd = input(f'{bcolors.COMMAND}Command: {bcolors.END}')
    process_command(cmd, game)