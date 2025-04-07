from __future__ import annotations
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
    DISCARD = 'discard'

class bcolors:
    END = '\033[0m'
    END_FG = '\033[39m'
    END_BG = '\033[49m'
    # UI
    TITLE_BG = '\033[48;2;73;65;130m'
    TITLE = '\033[38;2;120;100;198m'
    HEALTH = '\033[31m'
    WEAPON = '\033[93m'
    MONSTER = '\033[92m'
    COMMAND = '\033[94m'
    # Suits
    CLUB = '\033[38;2;0;138;255m'
    DIAMOND = '\033[38;2;255;106;0m'
    HEART = '\033[38;2;255;0;0m'
    SPADE = '\033[38;2;0;0;0m'
    # ERR
    ERROR = '\033[38;2;128;0;0m'
    WARNING = '\033[38;2;128;53;0m'


CLUB_OPTIONS = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
DIAMOND_OPTIONS = 2, 3, 4, 5, 6, 7, 8, 9, 10
HEART_OPTIONS = 2, 3, 4, 5, 6, 7, 8, 9, 10
SPADE_OPTIONS = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14

SUIT_OPTIONS = CLUB_OPTIONS, DIAMOND_OPTIONS, HEART_OPTIONS, SPADE_OPTIONS

CARD_NAMES = "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"
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

    def __hash__(self):
        return hash((self.suit, self.value))

    def __eq__(self, other: Card):
        return other.suit == self.suit and other.value == self.value

    def __lt__(self, other: Card):
        return self.suit <= other.suit and self.value < other.value

    def __leq__(self, other: Card):
        return self.suit <= other.suit and self.value <= other.value

class ScoundrelGame:

    def __init__(self) -> None:
        self._player_health: int = 20
        self._player_weapon: Card | None = None

        self._dungeon: list[Card] = []
        self._room: list[Card] = []
        self._defeated_monsters: list[Card] = []
        self._discard: list[Card] = []

        self._has_fled: bool = False
        self._has_healed: bool = False
        self._game_finished: bool = False

    # -- GAME PROPERTIES --

    @property
    def is_finished(self) -> bool:
        return self._game_finished
    
    @property
    def has_won(self) -> bool:
        return self._game_finished and self._player_health != 0
    
    @property
    def has_lost(self) -> bool:
        return self._game_finished and self._player_health == 0

    @property
    def health(self) -> int:
        return self._player_health
    
    @property
    def weapon(self) -> Card | None:
        return self._player_weapon
    
    @property
    def monster(self) -> int | None:
        return None if not self._defeated_monsters else self._defeated_monsters[-1].value
    
    # -- GAME LOOP --

    def setup(self):
        self._player_health = 20
        self._player_weapon = None
        self._defeated_monsters = []

        self._game_finished = False

        self._dungeon = [Card(Suit(suit), value) for suit in range(4) for value in SUIT_OPTIONS[suit]]
        shuffle(self._dungeon)
        self.start_turn()
    
    def start_turn(self):
        if self._player_health == 0:
            self._game_finished = True
            return

        if len(self._room) > 1:
            return

        if not self._dungeon:
            self._game_finished = True
            if self._player_weapon is not None:
                self._discard.extend(self._defeated_monsters)
                self._discard.append(self._player_weapon)
                self._player_weapon = None
                self._defeated_monsters = []
            return

        self._has_fled = False
        self._has_healed = False
        while len(self._room) < 4 and self._dungeon:
            self._room.append(self._dungeon.pop()) 

    # -- ACTIONS --

    def can_get_card(self, idx: Literal[0, 1, 2, 3]) -> bool:
        return 0 <= idx < len(self._room)

    def peek_card(self, idx: Literal[0, 1, 2, 3]) -> Card | None:
        if not (0 <= idx < len(self._room)):
            return None
        return self._room[idx]

    def get_card(self, idx: Literal[0, 1, 2, 3]) -> Card | None:
        if not (0 <= idx < len(self._room)):
            return None
        card = self._room.pop(idx)

        return card
    
    def can_swap_cards(self, idx_a: Literal[0, 1, 2, 3], idx_b: Literal[0, 1, 2, 3]) -> bool:
        return 0 <= idx_a < len(self._room) and 0 <= idx_b < len(self._room)
    
    def swap_cards(self, idx_a: Literal[0, 1, 2, 3], idx_b: Literal[0, 1, 2, 3]):
        if idx_a >= len(self._room) or idx_b >= len(self._room):
            raise KeyError(f"The room only has {len(self._room)} cards in it and cannot swap {idx_a}<->{idx_b}")
        
        if idx_a == idx_b:
            return
        
        self._room[idx_a], self._room[idx_b] = self._room[idx_b], self._room[idx_a]

    def can_fight_card(self, card: Card) -> bool:
        return card.suit == Suit.CLUB or card.suit == Suit.SPADE

    def fight_card(self, card: Card, with_weapon: bool = False):
        if card.suit != Suit.CLUB and card.suit != Suit.SPADE:
            raise ValueError(f"{card} cannot be fought")

        lowest_monster_strength = 999 if not self._defeated_monsters else self._defeated_monsters[-1].value
        with_weapon = with_weapon and self._player_weapon is not None and card.value < lowest_monster_strength

        player_weapon_strength = 0 if not with_weapon else self._player_weapon.value

        diff = max(0, card.value - player_weapon_strength)
        self._player_health = max(0, self._player_health - diff)
        if with_weapon:
            self._defeated_monsters.append(card)
        else:
            self.discard_card(card)

    def can_use_card(self, card: Card) -> bool:
        return self.can_equip_card(card) or self.can_heal(card)

    def can_equip_card(self, card: Card) -> bool:
        return card.suit == Suit.DIAMOND

    def equip_card(self, card: Card) -> None:
        if card.suit != Suit.DIAMOND:
            raise ValueError(f"{card} cannot be equiped")
        
        if self._player_weapon is not None:
            self._discard.extend(self._defeated_monsters)
            self.discard_card(self._player_weapon)

        self._defeated_monsters = []
        self._player_weapon = card

    def can_heal(self, card: Card) -> bool:
        return card.suit == Suit.HEART

    def consume_card(self, card: Card) -> None:
        if card.suit != Suit.HEART:
            raise ValueError(f"{card} cannot be consumed")

        if not self._has_healed:
            self._player_health = min(20, self._player_health + card.value)

        self._has_healed = True
        self.discard_card(card)

    def can_flee(self) -> bool:
        return len(self._room) >= 4 and not self._has_fled
    
    def flee(self) -> None:
        if len(self._room) < 4 or self._has_fled:
            return

        shuffle(self._room)
        self._dungeon.extend(self._room)
        self._room = []
        while len(self._room) < 4 and self._dungeon:
            self._room.append(self._dungeon.pop(0))
        self._has_fled = True

    def discard_card(self, card: Card):
        if card in self._discard:
            raise ValueError('{card} has already been discarded')

        if card in self._dungeon:
            self._dungeon.remove(card)
        if card in self._defeated_monsters:
            self._defeated_monsters.remove(card)
        if self._player_weapon is not None and card == self._player_weapon:
            self._player_weapon = None
            self._discard.extend(self._defeated_monsters)
            self._defeated_monsters = []
        self._discard.append(card)

def check_if_valid_command(command: str, args: list[str]) -> bool:    
    if command in {'0', '1', '2', '3'}:
        return True

    if command not in Commands:
        print(f'{bcolors.ERROR}{command} is not a valid command{bcolors.END}', end='\t')
        return False

    if command == Commands.FLEE:
        return True

    if not args or args[0] not in {'0', '1', '2', '3'}:
        print('{bcolors.ERROR}Lacking required card position argument{bcolors.END}', end='\t')
        return False

    if command == Commands.SWAP and (len(args) < 2 or args[1] not in {'0', '1', '2', '3'}):
        print('{bcolors.ERROR}Swap command requires two valid card indices{bcolors.END}', end='\t')
        return False

    return True

def check_if_can_do_command(command: str, args: list[str], game: ScoundrelGame) -> bool:
    if command == Commands.FLEE:
        if not game.can_flee():
            print(f'{bcolors.ERROR}Unable to flee currently{bcolors.END}', end='\t')
            return False
        return True

    if command in {'0', '1', '2', '3'}:
        idx = int(command)
        if not game.can_get_card(idx):
            print(f'{bcolors.ERROR}Room does not have card {idx}{bcolors.END}', end='\t')
            return False
        card = game.peek_card(idx)
        if game.can_use_card(card) or game.can_fight_card(card):
            return True
        print(f'{bcolors.ERROR}{card} has no uses currently{bcolors.END}', end='\t')
        return False
    

    idx = int(args[0])
    if not game.can_get_card(idx):
        print(f'{bcolors.ERROR}Room does not have card {idx}{bcolors.END}', end='\t\t')
        return False
    card = game.peek_card(idx)
    match command:
        case Commands.FIGHT:
            if not game.can_fight_card(card):
                print(f'{bcolors.ERROR}Cannot fight {card}{bcolors.END}', end='\t')
                return False
        case Commands.CONSUME:
            if not game.can_heal(card):
                print(f'{bcolors.ERROR}Unable to heal{bcolors.END}', end='\t')
                return False
        case Commands.EQUIP:
            if not game.can_equip_card(card):
                print(f'{bcolors.ERROR}Cannot equip {card}{bcolors.END}', end='\t')
                return False
        case Commands.SWAP:
            idx_b = int(args[1])
            if not game.can_get_card(idx_b) or not game.can_swap_cards(idx, idx_b):
                print(f'{bcolors.ERROR}Cannot swap cards {idx} and {idx_b}{bcolors.END}', end='\t')
                return False
        case Commands.USE:
            if not game.can_use_card(card):
                print(f'{bcolors.ERROR}Cannot use {card}{bcolors.END}', end='\t')
                return False
        case _:
            # Should be possible during normal game flow
            print(f'{bcolors.ERROR}Invalid or Illformated Command and Args{bcolors.END}',end='\t')
            return False
    
    return True 


def run_command(command: str, args: list[str], game: ScoundrelGame):
    if command == Commands.FLEE:
        game.flee()
        return

    if command in {'0', '1', '2', '3'}:
        idx = int(command)
        card = game.get_card(idx)
        if card.suit == Suit.DIAMOND:
            game.equip_card(card)
        elif card.suit == Suit.HEART:
            game.consume_card(card)
        else:
            with_weapon = args and args[0] in {'y', 'yes', 'weapon', 'use', '+'}
            game.fight_card(card, with_weapon)
        return
    else:
        idx = int(args[0])
    
    match command:
        case Commands.FIGHT:
            card = game.get_card(idx)
            with_weapon = len(args) >= 2 and args[1] in {'y', 'yes', 'weapon', 'use', '+'}
            game.fight_card(card, with_weapon)
        case Commands.CONSUME:
            card = game.get_card(idx)
            game.consume_card(card)
        case Commands.EQUIP:
            card = game.get_card(idx)
            game.equip_card(card)
        case Commands.SWAP:
            idx_b = int(args[1])
            game.swap_cards(idx, idx_b)
        case Commands.USE:
            card = game.get_card(idx)
            if card.suit == Suit.DIAMOND:
                game.equip_card(card)
            else:
                game.consume_card(card)

def print_game(turn: int, game: ScoundrelGame):
    print(f'{bcolors.TITLE_BG}|----------{bcolors.TITLE}SCOUNDREL{bcolors.END_FG}----------|{bcolors.END_BG}')
    print(f'|----------TURN:{" "*(4 - len({turn}))}{turn}----------|')
    print(f'|----------{bcolors.HEALTH}HEALTH:{f" {game.health}" if game.health < 10 else game.health}{bcolors.END}----------|')
    print(f'|-ROOM------{bcolors.WEAPON}WEAPON{bcolors.END}---{bcolors.MONSTER}DEFEATED{bcolors.END}-|')
    length = max(len(game._room), len(game._defeated_monsters))
    for idx in range(length):
        card = game.peek_card(idx)
        card_str = f"{idx}-{card}{'-' if card.value != 10 else ''}" if card is not None else '-------'

        weapon = game.weapon
        weapon_str = '-------' if weapon is None or idx != 0 else f"{weapon}{'-' if weapon.value != 10 else ''}"

        monster = None if len(game._defeated_monsters) <= idx else game._defeated_monsters[idx]
        monster_str = '-------' if monster is None else f"{monster}{'-' if monster.value != 10 else ''}"

        print(f'|-{card_str}--{weapon_str}--{monster_str}-|')
    print(f'{bcolors.TITLE_BG}|----------{bcolors.TITLE}SCOUNDREL{bcolors.END_FG}----------|{bcolors.END_BG}')

def print_finish(turn: int, game: ScoundrelGame):
    print(f'{bcolors.TITLE_BG}|----------{bcolors.TITLE}SCOUNDREL{bcolors.END_FG}----------|{bcolors.END_BG}')
    print(f'{bcolors.TITLE_BG}|----------TURN:{" "*(4 - len({turn}))}{turn}----------|{bcolors.END_BG}')
    print(f'{bcolors.TITLE_BG}|----------{bcolors.TITLE}{'YOU   WON' if game.has_won else 'YOU  LOST'}{bcolors.END_FG}----------|{bcolors.END_BG}')
    print(f'{bcolors.TITLE_BG}|----------{bcolors.TITLE}SCOUNDREL{bcolors.END_FG}----------|{bcolors.END_BG}')

def play():
    game = ScoundrelGame()
    game.setup()
    turn = 0
    game.start_turn()
    while not game.is_finished:
        turn += 1
        print_game(turn, game)
        player_input = input(f'{bcolors.COMMAND}Command: {bcolors.END}')
        command, *args = player_input.lower().split(' ')
        valid_command = check_if_valid_command(command, args)
        if not valid_command:
            print(f'{bcolors.WARNING}Invalid Command, Try Again{bcolors.END}')
            continue
        valid_command = check_if_can_do_command(command, args, game)
        if not valid_command:
            print(f'{bcolors.WARNING}Try Again{bcolors.END}')
            continue
        run_command(command, args, game)
        game.start_turn()
    print_finish(turn, game)

if __name__ == '__main__':
    play()