from cards import Deck, hand_value


class EmptyDeck(Exception):
    """Raised when a card is needed but the deck has none left."""


def is_blackjack(hand):
    """A natural: exactly two cards totalling 21."""
    return len(hand) == 2 and hand_value(hand) == 21


def draw_card(deck, hand, who, hidden=False):
    """Draw one card into hand and announce it. Raises EmptyDeck if none left."""
    card = deck.draw()
    if card is None:
        raise EmptyDeck
    hand.append(card)
    if hidden:
        print(f"{who} draws a card")
    else:
        print(f"{who} draws {card[0]}{card[1]}")


class Blackjack:
    def __init__(self):
        self.chips = 100
        self.bet = 0
        self.settled = True  # no round in progress yet

    def show(self, player, dealer, hide=True):
        shown_dealer = ["??"] if hide else [f"{r}{s}" for r, s in dealer]
        print("Dealer:", " ".join(shown_dealer))
        print("Player:", " ".join(f"{r}{s}" for r, s in player),
              "=", hand_value(player))

    def ask_bet(self):
        """Prompt until a whole number from 1 to self.chips. None = quit."""
        while True:
            raw = input(f"Bet (1-{self.chips}, q to quit): ").strip().lower()
            if raw == "q":
                return None
            if raw.isascii() and raw.isdigit():
                bet = int(raw)
                if 1 <= bet <= self.chips:
                    return bet
            print(f"Enter a whole number from 1 to {self.chips}.")

    def finish(self, delta, message):
        """Single exit point for a finished round: settle once, report, end."""
        if self.settled:
            raise RuntimeError("Round already settled")
        self.settled = True
        self.chips += delta
        change = f"{delta:+d} chips" if delta else "no chip change"
        print(f"{message} ({change}) Chips: {self.chips}")
        return True

    def round(self):
        print(f"\nChips: {self.chips}")
        bet = self.ask_bet()
        if bet is None:
            return False
        self.bet = bet
        self.settled = False
        try:
            return self._play()
        except EmptyDeck:
            return self.finish(0, "Deck ran out of cards. Round void, bet returned.")

    def _play(self):
        deck = Deck()
        player, dealer = [], []
        draw_card(deck, player, "Player")
        draw_card(deck, player, "Player")
        draw_card(deck, dealer, "Dealer", hidden=True)
        draw_card(deck, dealer, "Dealer", hidden=True)
        self.show(player, dealer)

        # Naturals are settled immediately, before the player can act.
        p_nat, d_nat = is_blackjack(player), is_blackjack(dealer)
        if p_nat or d_nat:
            self.show(player, dealer, hide=False)
            if p_nat and d_nat:
                return self.finish(0, "Both have blackjack. Push.")
            if p_nat:
                return self.finish(self.bet * 3 // 2, "Blackjack! Player wins 3:2.")
            return self.finish(-self.bet, "Dealer has blackjack. Dealer wins.")

        # Player turn
        while hand_value(player) < 21:
            key = input("[h]it [s]tand [q]uit: ").strip().lower()
            if key == "q":
                return False
            if key == "s":
                break
            if key == "h":
                draw_card(deck, player, "Player")
                self.show(player, dealer)
                if hand_value(player) > 21:
                    return self.finish(-self.bet, "Bust. Dealer wins.")
            else:
                print(f"Invalid command '{key}'. Use h, s or q.")

        # Dealer turn: draw until 17 or more
        while hand_value(dealer) < 17:
            draw_card(deck, dealer, "Dealer")

        self.show(player, dealer, hide=False)
        pv, dv = hand_value(player), hand_value(dealer)
        if dv > 21:
            return self.finish(self.bet, "Dealer busts. Player wins.")
        if pv > dv:
            return self.finish(self.bet, "Player wins.")
        if pv < dv:
            return self.finish(-self.bet, "Dealer wins.")
        return self.finish(0, "Push.")

    def run(self):
        print("Blackjack ΓÇö starting chips:", self.chips)
        while self.chips > 0:
            if not self.round():
                return
            if self.chips <= 0:
                print("Out of chips. Game over.")
                return
            if input("Play again? [y/n]: ").strip().lower() != "y":
                return