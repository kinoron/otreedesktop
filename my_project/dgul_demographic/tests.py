from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random

class PlayerBot(Bot):
    def play_round(self):
        random_age = random.randint(18, 65)  # ランダムな年齢を生成
        random_gender = random.choice(["男性", "女性", "その他", "回答したくない"])  # ランダムな性別を生成
        if self.player.round_number == 1:
            yield Survey, dict(
                age=random_age,
                gender=random_gender,
            )
        
        yield SVO, dict(
            svoA=random.randint(1, 9)  # ランダムなSVOの値を生成
        )


