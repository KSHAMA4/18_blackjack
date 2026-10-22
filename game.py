from cards import Deck, hand_value

BET = 10


def is_blackjack(hand):
    """A natural: exactly two cards totalling 21."""
    return len(hand) == 2 and hand_value(hand) == 21


class Blackjack:
    def __init__(self):
        self.chips = 100

    def show(self, player, dealer, hide=True):
        shown_dealer = ["??"] if hide else [f"{r}{s}" for r, s in dealer]
        print("Dealer:", " ".join(shown_dealer))
        print("Player:", " ".join(f"{r}{s}" for r, s in player),
              "=", hand_value(player))

    def finish(self, delta, message):
        """Single exit point for a finished round: apply chips, report, end."""
        self.chips += delta
        print(f"{message} Chips: {self.chips}")
        return True

    def round(self):
        deck = Deck()
        player = [deck.draw(), deck.draw()]
        dealer = [deck.draw(), deck.draw()]
        self.show(player, dealer)

        # Naturals are settled immediately, before the player can act.
        p_nat, d_nat = is_blackjack(player), is_blackjack(dealer)
        if p_nat or d_nat:
            self.show(player, dealer, hide=False)
            if p_nat and d_nat:
                return self.finish(0, "Both have blackjack. Push.")
            if p_nat:
                return self.finish(BET * 3 // 2, "Blackjack! Player wins 3:2.")
            return self.finish(-BET, "Dealer has blackjack. Dealer wins.")

        # Player turn
        while hand_value(player) < 21:
            key = input("[h]it [s]tand [q]uit: ").strip().lower()
            if key == "q":
                return False
            if key == "s":
                break
            if key == "h":
                player.append(deck.draw())
                self.show(player, dealer)
                if hand_value(player) > 21:
                    return self.finish(-BET, "Bust. Dealer wins.")

        # Dealer turn: draw until 17 or more
        while hand_value(dealer) < 17:
            dealer.append(deck.draw())

        self.show(player, dealer, hide=False)
        pv, dv = hand_value(player), hand_value(dealer)
        if dv > 21:
            return self.finish(BET, "Dealer busts. Player wins.")
        if pv > dv:
            return self.finish(BET, "Player wins.")
        if pv < dv:
            return self.finish(-BET, "Dealer wins.")
        return self.finish(0, "Push.")

    def run(self):
        print("Blackjack ΓÇö starting chips:", self.chips)
        while self.chips > 0:
            if not self.round():
                return
            if input("Play again? [y/n]: ").strip().lower() != "y":
                return