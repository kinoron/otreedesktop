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
        label="",
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
    # 理解度クイズの回答を保存する変数
    quiz_role = models.StringField(
        label="あなたの今回の役割として正しいものを選んでください：",
        choices=[
            ['send', '送る人'],
            ['receive', 'もらう人']
        ],
        widget=widgets.RadioSelect  # ラジオボタン形式にする
    )



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
class Consent(Page):
    pass

# --- ページクラスの中 ---
class Introduction(Page):
    form_model = 'player'
    form_fields = ['quiz_role']

    @staticmethod
    def error_message(player: Player, values):
        # 正解の定義：IDが1なら'send'、それ以外なら'receive'
        correct_answer = 'send' if player.role == C.ALLOCATOR_ROLE else 'receive'
        
        # 参加者の入力(values['quiz_role'])が正解と違う場合、エラー文を返す
        if values['quiz_role'] != correct_answer:
            return '回答が間違っています。もう一度説明を確認して回答し直してください。'


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
    body_text = "送る人が金額を考えています。しばらくお待ちください。"
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


page_sequence = [Consent, Introduction, Offer, OfferWaitPage, Respond, ResultsWaitPage, Results]