from otree.api import *


doc = """
Dictator Game with Ultimatum Game
"""


class C(BaseConstants):
    NAME_IN_URL = 'dgul'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    ALLOCATOR_ROLE = 'Allocator'
    RESPONDER_ROLE = 'Responder'
    ENDOWMENT = cu(500)



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    game_mode = models.StringField(
        choices=['dictator', 'ultimatum'],
        doc="ゲームの条件（dictator: 独裁者, ultimatum: 最後通牒）"
    )

    kept_amount = models.CurrencyField(
        doc="""Amount allocator decided to keep for himself""",
        min=0,
        max=C.ENDOWMENT,
    )

    offered_amount = models.IntegerField(
        label="相手にいくら分け合いますか？",
        min=0, max=C.ENDOWMENT
    )

    # 最後通牒ゲーム用：受け入れ（True=Accept, False=Reject）
    accepted = models.BooleanField(
        label="この提案を受け入れますか？",
        choices=[
            [True, '受け入れる'],
            [False, '拒否する']
        ]
    )


class Player(BasePlayer):
    pass



####funcions

def creating_session(subsession: Subsession):
    # subsession.group_randomly()  # プレイヤーをランダムにグループ分け
    # セッション開始時に、グループごとに条件を割り当てる（例：ランダムに半々）
    import random
    for group in subsession.get_groups():
        # configから取得するか、ランダムに決定
        group.game_mode = random.choice(['dictator', 'ultimatum'])

def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    
    group.kept_amount = C.ENDOWMENT - group.offered_amount
    
    if group.game_mode == 'dictator':
        # 独裁者ゲーム：提案がそのまま通る
        p1.payoff = group.kept_amount
        p2.payoff = group.offered_amount
    elif group.game_mode == 'ultimatum':
        # 最後通牒ゲーム：応答者の選択に依存
        if group.accepted:
            p1.payoff = group.kept_amount
            p2.payoff = group.offered_amount
        else:
            p1.payoff = 0
            p2.payoff = 0

# PAGES
class RoleIntroduction(Page):
    """役割とゲームルールの説明画面"""
    pass


class Offer(Page):
    """提案者（Player 1）が額を決定する画面"""
    form_model = 'group'
    form_fields = ['offered_amount']

    @staticmethod
    def is_displayed(player: Player):
        # 提案者のみに表示
        return player.role == C.ALLOCATOR_ROLE


class OfferWaitPage(WaitPage):
    title_text = "待機中"
    body_text = "提案者が金額を考えています。しばらくお待ちください。"
    @staticmethod
    def is_displayed(player: Player):
        # 応答者のみに表示
        return player.role == C.RESPONDER_ROLE


class Respond(Page):
    """応答者が意思決定する画面"""
    form_model = 'group'
    form_fields = ['accepted']

    @staticmethod
    def is_displayed(player: Player):
        # 応答者かつ、最後通牒ゲームの場合のみ表示
        return player.role == C.RESPONDER_ROLE and player.group.game_mode == 'ultimatum'


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    title_text = "集計中"
    body_text = "結果を計算しています。"


class Results(Page):
    """結果画面"""
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'my_payoff': player.payoff,
            'role': '提案者' if player.role == C.ALLOCATOR_ROLE else '応答者',
        }


page_sequence = [RoleIntroduction, Offer, OfferWaitPage, Respond, ResultsWaitPage, Results]