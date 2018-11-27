import numpy as np


class Deck:
    _ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    _suits = ["clubs", "diamonds", "hearts", "spades"]
    _values = {"A":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}

    def __init__(self):
        self._cards = self._create_cards()

    @property
    def cards(self):
        return self._cards

    def _create_cards(self):
        return [(rank, suit, self._values[rank]) for rank in self._ranks for suit in self._suits]

    def shuffle(self):
        np.random.shuffle(self._cards)

    def deal_initial_cards(self, players):
        for player in players:
            player.hand.addCard(self.deal_card())
            player.hand.addCard(self.deal_card())

    def deal_card(self):
        return self.cards.pop(0)


class Hand:
    def __init__(self):
        self._cards = []
        self._total_value = 0
        self._status = "valid"

    @property
    def cards(self):
        return self._cards

    @property
    def total_value(self):
        return self._total_value

    @property
    def status(self):
        return self._status

    def set_status(self, status):
        self._status = status

    def addCard(self, card):
        self.cards.append(card)
        self._update_total_value(card[2])

    def _update_total_value(self, card_value):
        self._total_value += card_value


    def evaluate(self):
        if self.total_value > 21:
            return "busted"
     
class Player:
    def __init__(self, name, game):
        self._name = name
        self._hand = Hand()
        self._game = game

    @property
    def name(self):
        return self._name

    @property
    def hand(self):
        return self._hand

    @property
    def game(self):
        return self._game

    def hit(self):
        self.hand.addCard(self.game.deck.deal_card())
        if self.hand.evaluate() is "busted":
            self.game.end_turn()

    def stand(self):
        self.game.end_turn()


class Game:
    def __init__(self):
        self._deck = Deck()
        self._players = []
        self._turn = 0
        self._score = {}
        self._winners = ""

    @property
    def players(self):
        return self._players

    @property
    def score(self):
        return self._score

    @property
    def winners(self): 
        return self._winners

    @property
    def deck(self):
        return self._deck

    @property
    def turn(self):
        return self._turn

    def set_players(self, players):
        for player in players:
            self.players.append(Player(player, self))

    def run(self):
        self._deck.shuffle()
        self._deck.deal_initial_cards(self.players)

    def _dealer_turn(self): #Very dumb AI alwas hits until he is over a total card value of 17
        while self._players[self._turn].hand.total_value < 17:
            self._players[self._turn].hit()

        if self._players[self._turn].hand.evaluate() is not "busted":
            self._players[self._turn].stand()

    def _set_score(self):
        for player in self.players:
            if player.hand.evaluate() is not "busted":
                self.score[player] = player.hand.total_value
            else:
                self.score[player] = 0

    def _determine_winner(self):
        winners = []

        #Get player(s) with highest score(s)
        for player, score in self.score.items():
            if score == max(self.score.values()):
                player.hand.set_status("win")
                winners.append(player)
            else:
                player.hand.set_status("loss")

        #If multiple winners change their hand status to draw
        if len(winners) > 1:
            for player in winners:
                player.hand.set_status("draw")
        self._winners = winners

    def end_turn(self):
        if self._players[self._turn] == self._players[-1]: #Check if this player was the last player
            self._end_round()
        else:
            self._turn += 1
            self._dealer_turn() #To keep things simple, we will now let the dealer play
            
    def _end_round(self):
        self._set_score()
        self._determine_winner()
        