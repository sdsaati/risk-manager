from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal as d
from .models import Broker, Symbol, UserBroker, Trade


class TradeModelsTest(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(username="testuser", password="testpass")

   
        self.broker = Broker.objects.create(name="Binance", defaultCommission=d("0.01"))


        self.symbol = Symbol.objects.create(name="BTCUSDT", broker=self.broker, commission=d("0.02"))


        self.user_broker = UserBroker.objects.create(
            user=self.user,
            broker=self.broker,
            balance=d("10000"),
            reserve=d("1000"),
            reservePercent=d("10"),
            riskPercent=d("5")
        )

    def test_broker_str(self):
        self.assertIn("Binance", str(self.broker))

    def test_symbol_str(self):
        self.assertEqual(str(self.symbol), "BTCUSDT(0.02)")

    def test_user_broker_properties(self):
        self.assertEqual(self.user_broker.defined_reserve, d("1000"))
        self.assertEqual(self.user_broker.available_balance, d("9000"))
        self.assertEqual(self.user_broker.risk, d("450"))  # 5% of 9000

    def test_trade_creation_and_profit_win(self):
        trade = Trade.objects.create(
            ub=self.user_broker,
            symbol=self.symbol,
            stop=d("90"),
            entry=d("100"),
            target=d("120"),
            result=True,
            stop_percent=d("10"),
            risk_reward=d("2"),
            amount=d("1000")
        )
        self.assertAlmostEqual(trade.profit(), d("200.0"), places=2)  # (1000*0.1*2) - (1000*0.02)

    def test_trade_profit_loss(self):
        trade = Trade.objects.create(
            ub=self.user_broker,
            symbol=self.symbol,
            stop=d("90"),
            entry=d("100"),
            target=d("120"),
            result=False,
            stop_percent=d("10"),
            risk_reward=d("2"),
            amount=d("1000")
        )
        self.assertAlmostEqual(trade.profit(), d("-80.0"), places=2)  # -(1000*0.1 - 1000*0.02)

    def test_commission_fallback(self):
        symbol_no_comm = Symbol.objects.create(name="ETHUSDT", broker=self.broker, commission=None)
        trade = Trade.objects.create(
            ub=self.user_broker,
            symbol=symbol_no_comm,
            stop_percent=d("10"),
            risk_reward=d("2"),
            amount=d("1000")
        )
        self.assertEqual(trade.commission, d("0.01"))


