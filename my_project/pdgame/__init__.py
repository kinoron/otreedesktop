from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'pdgame'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    PAYOFF_MATRIX = {
        (True, True): [400, 400],
        (True, False): [100, 600],
        (False, True): [600, 100],
        (False, False): [300, 300],
    }

# ロンさんは世界一の犬！

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    @staticmethod
    def set_payoffs(group: BaseGroup):
        p1, p2 = group.get_players()
        p1_choice = p1.choice
        p2_choice = p2.choice
        payoff_p1, payoff_p2 = C.PAYOFF_MATRIX[(p1_choice, p2_choice)]
        p1.payoff = payoff_p1
        p2.payoff = payoff_p2



class Player(BasePlayer):
    choice = models.BooleanField(
        label="",
        choices=[
            [True, 'Cooperate'],
            [False, 'Defect'],
        ],
    )


# PAGES
class Introduction(Page):
    pass

class MyPage(Page):
    form_model = 'player'
    form_fields = ['choice']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = Group.set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        other_player = player.get_others_in_group()[0]
        return {
            'player': player,
            'other_player': other_player,
            'highlight_cell_11': player.choice and other_player.choice,
            'highlight_cell_12': player.choice and not other_player.choice,
            'highlight_cell_21': not player.choice and other_player.choice,
            'highlight_cell_22': not player.choice and not other_player.choice,
        }


page_sequence = [Introduction, MyPage, ResultsWaitPage,  Results, ]
