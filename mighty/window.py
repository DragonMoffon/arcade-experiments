from mighty.data import WordType, Word, Blank, FillIn, Card, WORDS, FILLINS
import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


CARD_HEIGHT = 120
CARD_WIDTH = 0.714 * CARD_HEIGHT  # mtg card ratio lmao

FRAME_PADDING = 40 + CARD_WIDTH / 2
CARD_PADDING = 10
CENTER_PADDING = 20 + CARD_WIDTH / 2

WORD_HAND_MAX = 7
FILL_HAND_MAX = 4
    

def score_card(card: Card):
    # Score the internal values of the card (maybe)
    for blank, word in zip(card.fill_in.blanks, card.blanks, strict=True):
        pass

def score_verse(phrases: list[Card]):
    # Score the phrase
    pass

def draw_card(card: Card):
    pass

def draw_word_card(word: Word):
    pass

def draw_fill_card(fill: FillIn):
    pass

class MightyWindow(arcade.Window):

    def __init__(self):
        super().__init__(1280, 720, "TEMPLATE")
        self.word_hand: list[Word] = list(WORDS)
        self.fill_hand: list[FillIn] = list(FILLINS)

        self.selected_fill: FillIn = None
        self.selected_words: list[Word] = []
        
        self.played_cards: list[Card] = []
        
        self.hovered_item: FillIn | Word | None = None

        self.word_text = arcade.Text('', 0, 0, arcade.color.WHITE, anchor_x='center', anchor_y='center')
        self.fill_text = arcade.Text('', 0, 0, arcade.color.WHITE, anchor_x='center', anchor_y='center', align='center', width=CARD_WIDTH - 10, multiline=True)

        self.word_deck: list = list(WORDS)
        self.fill_deck: list = list(FILLINS)

    def on_draw(self):
        self.clear()

        if self.hovered_item is None:
            arcade.draw_point(self.center_x, CARD_HEIGHT * 0.5, arcade.color.WHITE, 16)
        
        size = self.width / 2.0 - CENTER_PADDING - FRAME_PADDING
        if self.word_hand:
            anchor = self.center_x + CENTER_PADDING + CARD_WIDTH / 2.0
            count = len(self.word_hand)
            step = min(CARD_WIDTH + CARD_PADDING, 1 / count * size)
            for idx, word in enumerate(self.word_hand):
                x = anchor + idx * step
                y = CARD_HEIGHT * 0.75
                c = arcade.color.RUBY_RED
                if word == self.hovered_item:
                    y = CARD_HEIGHT * 1.25
                    c = arcade.color.RAZZLE_DAZZLE_ROSE

                if word in self.selected_words:
                    y = max(CARD_HEIGHT * 1.0, y)
                    self.word_text.text = str(self.selected_words.index(word) + 1)
                    self.word_text.position = (x, y + CARD_HEIGHT / 2.0 + 10)
                    self.word_text.draw()
                
                arcade.draw_rect_filled(arcade.XYWH(x, y, CARD_WIDTH, CARD_HEIGHT), c)
                arcade.draw_rect_outline(arcade.XYWH(x, y, CARD_WIDTH, CARD_HEIGHT), arcade.color.WHITE)
                self.word_text.text = word.text
                self.word_text.position = (x, y)
                self.word_text.draw()

        if self.fill_hand:
            anchor = self.center_x - CENTER_PADDING - CARD_WIDTH / 2.0
            count = len(self.fill_hand)
            step = min(CARD_WIDTH + CARD_PADDING, 1.0 / count * size)
            for idx, fill in enumerate(self.fill_hand):
                x = anchor - idx * step
                y = CARD_HEIGHT * 0.75
                c = arcade.color.NAVY_BLUE
                if fill == self.hovered_item:
                    y = CARD_HEIGHT * 1.0
                    c = arcade.color.BABY_BLUE
                if fill == self.selected_fill:
                    y = max(CARD_HEIGHT * 0.8, y)
                    arcade.draw_point(x, y + CARD_HEIGHT / 2.0 + 10, arcade.color.BABY_BLUE, 10)
                
                arcade.draw_rect_filled(arcade.XYWH(x, y, CARD_WIDTH, CARD_HEIGHT), c)
                arcade.draw_rect_outline(arcade.XYWH(x, y, CARD_WIDTH, CARD_HEIGHT), arcade.color.WHITE)
                self.fill_text.text = " ".join(word or "[  ]" for word in fill.words)
                self.fill_text.position = (x, y)
                self.fill_text.draw()

        if self.played_cards:
            count = len(self.played_cards)
            size = self.width - 2*FRAME_PADDING
            step = min(CARD_WIDTH + CARD_PADDING, 1 / count * size)
            anchor = self.center_x - step * (0.0 if count == 1 else count - 1) / 2.0
            for idx, card in enumerate(self.played_cards):
                x = anchor + step * idx
                y = self.center_y

                arcade.draw_rect_filled(arcade.XYWH(x, y, CARD_WIDTH, CARD_HEIGHT), arcade.color.PURPLE_MOUNTAIN_MAJESTY)
                arcade.draw_rect_outline(arcade.XYWH(x, y, CARD_WIDTH, CARD_HEIGHT), arcade.color.WHITE)
                self.fill_text.text = card.text
                self.fill_text.position = (x, y)
                self.fill_text.draw()


    def draw_word(self):
        if len(self.word_hand) >= WORD_HAND_MAX:
            return
        self.word_hand.append(self.word_deck.pop(-1))
        if not self.word_deck:
            self.word_deck = list(WORDS)
        
    def draw_fill(self):
        if len(self.fill_hand) >= FILL_HAND_MAX:
            return
        self.fill_hand.append(self.fill_deck.pop(-1))
        if not self.fill_deck:
            self.fill_deck = list(FILLINS)

    def on_key_press(self, symbol, modifiers):
        match symbol:
            case arcade.key.LEFT:
                self.hover_left()
            case arcade.key.RIGHT:
                self.hover_right()
            case arcade.key.UP:
                self.select()
            case arcade.key.DOWN:
                self.deselect()

    def select(self):
        if self.hovered_item is None:
            if self.selected_fill is not None and len(self.selected_fill.blanks) == len(self.selected_words):
                # make card
                card = Card(self.selected_fill, self.selected_words)
                self.played_cards.append(card)
                self.fill_hand.remove(self.selected_fill)
                for word in self.selected_words:
                    self.word_hand.remove(word)
                self.selected_fill = None
                self.selected_words = []
                
            return
        elif self.hovered_item in self.fill_hand:
            if self.selected_fill is not None:
                self.selected_words = []
            self.selected_fill = self.hovered_item # just override
        elif self.selected_fill is not None and self.hovered_item in self.word_hand:
            if self.hovered_item in self.selected_words:
                self.selected_words.remove(self.hovered_item)
            elif len(self.selected_words) >= len(self.selected_fill.blanks):
                return
            else:
                self.selected_words.append(self.hovered_item)
            

    def deselect(self):
        if self.hovered_item == self.selected_fill:
            self.selected_fill = None
            self.selected_words = [] # hmm maybe not?? Maybe just crop
        elif self.hovered_item in self.selected_words:
            self.selected_words.remove(self.hovered_item)
        
    def hover_left(self):
        if self.hovered_item is None:
            if self.fill_hand:
                self.hovered_item = self.fill_hand[0]
            elif self.word_hand:
                self.hovered_item = self.word_hand[-1]
        elif self.hovered_item in self.fill_hand:
            idx = self.fill_hand.index(self.hovered_item) # EWWWW
            if idx + 1 >= len(self.fill_hand):
                if not self.word_hand:
                    self.hovered_item = None
                else:
                    self.hovered_item = self.word_hand[-1]
            else:
                self.hovered_item = self.fill_hand[idx + 1]
        else:
            idx = self.word_hand.index(self.hovered_item) # EWWWW
            if idx <= 0:
                self.hovered_item = None
            else:
                self.hovered_item = self.word_hand[idx - 1]

    def hover_right(self):
        if self.hovered_item is None:
            if self.word_hand:
                self.hovered_item = self.word_hand[0]
            elif self.fill_hand:
                self.hovered_item = self.fill_hand[-1]
        elif self.hovered_item in self.fill_hand:
            idx = self.fill_hand.index(self.hovered_item) # EWWWW
            if idx <= 0:
                self.hovered_item = None
            else:
                self.hovered_item = self.fill_hand[idx - 1]
        else:
            idx = self.word_hand.index(self.hovered_item) # EWWWW
            if idx + 1 >= len(self.word_hand):
                if not self.fill_hand:
                    self.hovered_item = None
                else:
                    self.hovered_item = self.fill_hand[-1]
            else:
                self.hovered_item = self.word_hand[idx + 1]
    
    def on_update(self, delta_time: float):
        ...


def main():
    win = MightyWindow()
    win.run()
