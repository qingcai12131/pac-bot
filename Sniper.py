import argparse
import datetime
import json
from time import sleep

from halo import Halo

from style import style
from tx import TXN

ascii = """
  ______               ___            
 /_  __/________ _____/ (_)___  ____ _
  / / / ___/ __ `/ __  / / __ \/ __ `/
 / / / /  / /_/ / /_/ / / / / / /_/ / 
/_/_/_/__ \__,_/\__,_/_/_/ /_/\__, /  
 /_  __(_)___ ____  _________/____/   
  / / / / __ `/ _ \/ ___/ ___/        
 / / / / /_/ /  __/ /  (__  )         
/_/ /_/\__, /\___/_/  /____/          
      /____/                          
"""

parser = argparse.ArgumentParser(description='Set your Token and Amount example: "sniper.py -t 0x34faa80fec0233e045ed4737cc152a71e490e2e3 -a 0.2 -s 15"')
parser.add_argument('-t', '--token', help='str, Token for snipe e.g. "-t 0x34faa80fec0233e045ed4737cc152a71e490e2e3"')
parser.add_argument('-a', '--amount',default=0, help='float, Amount in Bnb to snipe e.g. "-a 0.1"')
parser.add_argument('-tx', '--txamount', default=1, nargs="?", const=1, type=int, help='int, how mutch tx you want to send? It Split your BNB Amount in e.g. "-tx 5"')
parser.add_argument('-hp', '--honeypot', action="store_true", help='Check if your token to buy is a Honeypot, e.g. "-hp" or "--honeypot"')
parser.add_argument('-nb', '--nobuy', action="store_true", help='No Buy, Skipp buy, if you want to use only TakeProfit/StopLoss/TrailingStopLoss')
parser.add_argument('-tp', '--takeprofit', default=0, nargs="?", const=True, type=int, help='int, Percentage TakeProfit from your input BNB amount "-tp 50" ')
parser.add_argument('-sl', '--stoploss', default=0, nargs="?", const=True, type=int, help='int, Percentage Stop loss from your input BNB amount "-sl 50" ')
parser.add_argument('-tsl', '--trailingstoploss', default=0, nargs="?", const=True, type=int, help='int, Percentage Trailing-Stop-loss from your first Quote "-tsl 50" ')
parser.add_argument('-wb', '--awaitBlocks', default=0, nargs="?", const=True, type=int, help='int, Await Blocks before sending BUY Transaction "-ab 50" ')
parser.add_argument('-cmt', '--checkMaxTax',  action="store_true", help='get Token Tax and check if its higher.')
parser.add_argument('-cc', '--checkcontract',  action="store_true", help='Check is Contract Verified and Look for some Functions.')
parser.add_argument('-so', '--sellonly',  action="store_true", help='Sell all your Tokens from given address')
parser.add_argument('-bo', '--buyonly',  action="store_true", help='Buy Tokens with from your given amount')
parser.add_argument('-cl', '--checkliquidity',  action="store_true", help='with this arg you use liquidityCheck')
parser.add_argument('-dsec', '--DisabledSwapEnabledCheck',  action="store_true", help='this argument disabled the SwapEnabled Check!')
parser.add_argument('-by', '--by',  action="store_true", help='购买')
parser.add_argument('-ap', '--ap',  action="store_true", help='授权')
args = parser.parse_args()

# 购买金额
amount = 0.0001


class SniperBot():
    def __init__(self):
        self.parseArgs()
        self.settings = self.loadSettings()
        self.SayWelcome()

    # 加载配置文件
    def loadSettings(self):
        with open("Settings.json", "r") as settings:
            settings = json.load(settings)
        return settings

    # 打印
    def SayWelcome(self):
        # print(style().YELLOW + ascii + style().RESET)
        print(style().GREEN + "启动参数:" + style().RESET)
        print(style().BLUE + "---------------------------------" + style().RESET)
        print(style().YELLOW + "购买金额:", style().GREEN + str(self.amount) + " BNB" + style().RESET)
        print(style().YELLOW + "购买合约 :", style().GREEN + str(self.token) + style().RESET)

        print(style().YELLOW + "Transaction to send:", style().GREEN + str(self.tx) + style().RESET)
        print(style().YELLOW + "Amount per transaction :",
              style().GREEN + str("{0:.8f}".format(self.amountForSnipe)) + style().RESET)
        print(style().YELLOW + "购买等待区块 :", style().GREEN + str(self.wb) + style().RESET)

        if self.tsl != 0:
            print(style().YELLOW + "追踪止损百分比 :", style().GREEN + str(self.tsl) + style().RESET)
        if self.tp != 0:
            print(style().YELLOW + "获利百分比 :", style().GREEN + str(self.tp) + style().RESET)
        if self.sl != 0:
            print(style().YELLOW + "止损百分比 :", style().GREEN + str(self.sl) + style().RESET)
        print(style().BLUE + "---------------------------------" + style().RESET)

    def parseArgs(self):
        self.token = args.token
        if self.token == None:
            print(style.RED + "Please Check your Token argument e.g. -t 0x34faa80fec0233e045ed4737cc152a71e490e2e3")
            print("exit!")
            raise SystemExit

        self.amount = args.amount
        if args.nobuy != True:
            if not args.sellonly:
                if self.amount == 0:
                    print(style.RED + "Please Check your Amount argument e.g. -a 0.01")
                    print("exit!")
                    raise SystemExit

        self.tx = args.txamount
        self.amountForSnipe = float(self.amount) / float(self.tx)
        self.hp = args.honeypot
        self.wb = args.awaitBlocks
        self.tp = args.takeprofit
        self.sl = args.stoploss
        self.tsl = args.trailingstoploss
        self.cl = args.checkliquidity
        self.stoploss = 0
        self.takeProfitOutput = 0




    def getAccountBnbBalance(self):
        spinner = Halo(text='获取账户 BNB 余额', spinner='dots')
        spinner.start()
        value = self.TXN.getBnbBalance()
        print(style().GREEN + "\n当前账号 bnb 余额：" + str(value) + "BNB")
        spinner.stop()


    def awaitLiquidity(self, token):
        spinner = Halo(text='await Liquidity', spinner='dots')
        spinner.start()


        liq = self.TXN.getLiquidityBNB(token)[1]
        datetime_object = datetime.datetime.now()
        print(style().GREEN + "\n[LIQUIDTY] token:" + self.token + " 流动性:", style().YELLOW + str(round(liq, 3)) + "BNB, time: " + str(datetime_object))
        while True:
            # sleep(0.07)
            try:
                # self.TXN.getOutputfromBNBtoToken()[0]
                spinner.stop()
                break
            except Exception as e:
                if "UPDATE" in str(e):
                    print(e)
                    raise SystemExit
                continue
        # print(style().GREEN+"[DONE] 增加流动性!"+ style().RESET)



    # 禁用购买
    def awaitEnabledBuy(self):
        spinner = Halo(text='await Dev Enables Swapping', spinner='dots')
        spinner.start()
        while True:
            sleep(0.07)
            try:
                if self.TXN.checkifTokenBuyDisabled() == True:
                    spinner.stop()
                    break
            except Exception as e:
                if "UPDATE" in str(e):
                    print(e)
                    raise SystemExit
                continue
        print(style().GREEN + "[DONE] Swapping is Enabeld!" + style().RESET)

    # 授权
    def awaitApprove(self):
        spinner = Halo(text='await Approve', spinner='dots')
        spinner.start()
        self.TXN = TXN(self.token, self.amountForSnipe)
        tx = self.TXN.approve()
        spinner.stop()
        print(tx[1])
        if tx[0] != True:
            raise SystemExit

    # 等待区块
    def awaitBlocks(self):
        spinner = Halo(text='await Blocks', spinner='dots')
        spinner.start()
        waitForBlock = self.TXN.getBlockHigh() + self.wb
        while True:
            sleep(0.13)
            if self.TXN.getBlockHigh() > waitForBlock:
                spinner.stop()
                break
        print(style().GREEN + "[DONE] Wait Blocks finish!")

    # 购买
    def awaitBuy(self):
        spinner = Halo(text='await Buy', spinner='dots')
        spinner.start()

        for i in range(self.tx):
            spinner.start()
            self.TXN = TXN(self.token, self.amountForSnipe)
            tx = self.TXN.buy_token()
            spinner.stop()
            print(tx[1])
            if tx[0] != True:
                raise SystemExit

    # 启动
    def StartUP(self):
        self.TXN = TXN(self.token, self.amountForSnipe)

        # self.TXN.get_token_balance_by_token('0xbe0eb53f46cd790cd13851d5eff43d12404d33e8')
        self.getAccountBnbBalance()


        # 检查流动性
        self.awaitLiquidity(self.token)

        # 不买， 检查流动性
        # if args.nobuy != True:
        #     self.awaitLiquidity('0x183205Ef8740C1A74297B498A340Caf80e1f8c44')
        #     # 查询是否禁用
        #     if args.DisabledSwapEnabledCheck != True:
        #         self.awaitEnabledBuy()

        # 检查合约
        if args.checkcontract:
            self.CheckVerifyCode()

        # 检查合约
        if self.hp:
            honeyTax = self.TXN.checkToken(0x183205Ef8740C1A74297B498A340Caf80e1f8c44)
            print(style().YELLOW + "Checking Token..." + style().RESET)
            if honeyTax[2] == True:
                print(style.RED + "貔貅, exiting")
                raise SystemExit
            elif honeyTax[2] == False:
                print(style().GREEN + "[DONE] 不是貔貅!" + style().RESET)

        # 检查税
        if args.checkMaxTax:
            honeyTax = self.TXN.checkToken(self.token)
            if honeyTax[1] > self.settings["MaxSellTax"]:
                print(style().RED + "销售税过高 Settings.json, exiting!")
                raise SystemExit
            if honeyTax[0] > self.settings["MaxBuyTax"]:
                print(style().RED + "购买税过高 Settings.json, exiting!")
                raise SystemExit



        # python Sniper.py -t 0xF935389641087658241A1fD14A1878EfF74cC80B -a 0.001 -wb 10 -nb -cmt
        # python Sniper.py -t 0xcde1aa438136dbef0617c83cb12d1cde2fe29506 -a 0.001 -wb 10 -nb -cmt
        # python Sniper.py -t 0x2f05b9d5a9208b67e6a78a5602560d50de794d67 -a 0.001 -wb 10 -nb -cmt

        if args.by:
            self.awaitBuy()

        if args.ap:
            self.awaitApprove()


        # if args.nobuy != True:
        #     self.awaitBuy()

        #
        # if self.wb != 0:
        #     self.awaitBlocks()
        #
        # if self.cl == True:
        #     if self.fetchLiquidity() != False:
        #         pass
        #
        # # if args.nobuy != True:
        # # self.awaitBuy()
        #
        # sleep(
        #     7)  # Give the RPC/WS some time to Index your address nonce, make it higher if " ValueError: {'code': -32000, 'message': 'nonce too low'} "

        #
        # if self.tsl != 0 or self.tp != 0 or self.sl != 0:
        #     self.awaitMangePosition()

    print(style().GREEN + "[DONE] TradingTigers Sniper Bot finish!" + style().RESET)

SniperBot().StartUP()