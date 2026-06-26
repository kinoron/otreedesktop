import random
from otree.api import Currency as c, currency_range, expect, Bot
from . import *

class PlayerBot(Bot):
    def play_round(self):
        yield Consent
        yield Introduction, dict(quiz_role='send' if self.player.role == C.ALLOCATOR_ROLE else 'receive')
        if self.player.role == C.ALLOCATOR_ROLE:
            random_offer = random.randint(0, int(C.ENDOWMENT))
            yield Offer, dict(offered_amount=random_offer)

        if self.player.role == C.RESPONDER_ROLE and self.group.game_mode == 'ultimatum':
            # 応答者の意思決定
            # ここでは、オファーが半分以上なら受け入れ、そうでなければ拒否する戦略を採用
            if self.group.offered_amount >= int(C.ENDOWMENT) / 2:
                yield Respond, dict(accepted=True)
            else:
                yield Respond, dict(accepted=False)
        
        yield Results