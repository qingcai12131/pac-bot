import json
import time
from time import sleep
import datetime

from web3 import Web3
import random

from style import style
from decimal import *

# 薄饼路由
pancake_router = '0x10ED43C718714eb63d5aA57B78B54704E256024E'

class TXN():
    def __init__(self, token, quantity):
        self.w3 = self.connect()
        self.wlist = self.connectList()
        self.token = token
        self.address, self.private_key = self.setup_address()
        self.token_address = Web3.toChecksumAddress(token)
        self.token_contract = self.setup_token()
        self.slippage = self.setupSlippage()
        self.quantity = quantity
        self.MaxGasInBNB, self.gas_price = self.setupGas()


    # 检查合约
    def checkToken(self, token):
        token_address = Web3.toChecksumAddress(token)
        swapper_address = Web3.toChecksumAddress("0x18be7f977Ec1217B71D0C134FBCFF36Ea4366fCD")
        with open("./abis/BSC_Swapper.json") as f:
            contract_abi = json.load(f)
        swapper = self.w3.eth.contract(address=swapper_address, abi=contract_abi)

        tokenInfos = swapper.functions.getTokenInformations(token_address).call()
        buy_tax = round((tokenInfos[0] - tokenInfos[1]) / tokenInfos[0] * 100 ,2)
        sell_tax = round((tokenInfos[2] - tokenInfos[3]) / tokenInfos[2] * 100 ,2)
        if tokenInfos[5] and tokenInfos[6] == True:
            honeypot = False
        else:
            honeypot = True
        print(style.GREEN +"[TOKENTAX] token:" + token + " 购买税:", style().RED + str(buy_tax) + "%")
        print(style.GREEN +"[TOKENTAX] token:" + token + " 销售税:", style().RED + str(sell_tax) + "%")
        return buy_tax, sell_tax, honeypot

    def getSwapper(self, token):
        token_address = Web3.toChecksumAddress(token)
        swapper_address = Web3.toChecksumAddress("0x18be7f977Ec1217B71D0C134FBCFF36Ea4366fCD")
        with open("./abis/BSC_Swapper.json") as f:
            contract_abi = json.load(f)


        # r = random.randint(0, 9)
        # print(str(r))
        # w = self.wlist[r]

        swapper = self.w3.eth.contract(address=swapper_address, abi=contract_abi)
        return token_address, swapper


    def getLiquidityBNB(self, token):
        raw_call = 123
        token_address, swapper = self.getSwapper(token)
        try:
            raw_call = swapper.functions.fetchLiquidityETH(token_address).call()
        except Exception as e:
            #sleep(0.4)
            print(style.RED + str(e))
            datetime_object = datetime.datetime.now()
            if "No Liquidity Pool found!" in str(e):
                print(style.BLUE + "\ntoken:" + token + " 未获取到流动性，重试中" + str(datetime_object))
                return self.getLiquidityBNB(token)
            if "429 Client Error: Too Many Requests for url: https://bsc.mytokenpocket.vip/" in str(e):
                sleep(10)
                print(style.BLUE + "\ntoken:" + token + " 查询频繁，等待10s, 未获取到流动性，重试中" + str(datetime_object))
                return self.getLiquidityBNB(token)
        real = raw_call / (10**18)
        return raw_call, real

    # 连接钱包
    def connect(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        if keys["RPC"][:2].lower() == "ws":
            w3 = Web3(Web3.WebsocketProvider(keys["RPC"]))
        else:
            # w3 = Web3(Web3.HTTPProvider(keys["RPC"]))

            w3 = Web3(Web3.HTTPProvider(keys["RPC"]))
        return w3

        # 连接钱包

    def connectList(self):

        node1 = 'https://bsc-dataseed2.binance.org'
        node2 = 'https://bsc-dataseed3.binance.org'
        node3 = 'https://bsc-dataseed4.binance.org'
        node4 = 'https://bsc-dataseed2.defibit.io'
        node5 = 'https://bsc-dataseed3.defibit.io'
        node6 = 'https://bsc-dataseed4.defibit.io'
        node7 = 'https://bsc.mytokenpocket.vip'
        node8 = 'https://bsc.mytokenpocket.vip'
        node9 = 'https://bsc.mytokenpocket.vip'
        node10 = 'https://bsc.mytokenpocket.vip'


        w1 = Web3(Web3.HTTPProvider(node1))
        w2 = Web3(Web3.HTTPProvider(node2))
        w3 = Web3(Web3.HTTPProvider(node3))
        w4 = Web3(Web3.HTTPProvider(node4))
        w5 = Web3(Web3.HTTPProvider(node5))
        w6 = Web3(Web3.HTTPProvider(node6))
        w7 = Web3(Web3.HTTPProvider(node7))
        w8 = Web3(Web3.HTTPProvider(node8))
        w9 = Web3(Web3.HTTPProvider(node9))
        w10 = Web3(Web3.HTTPProvider(node10))


        return [w1, w2, w3, w4, w5, w6, w7, w8, w9, w10]

    # 设置 gas费
    def setupGas(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        return keys['MaxTXFeeBNB'], int(keys['GWEI_GAS'] * (10**9))

    # 地址
    def setup_address(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        if len(keys["metamask_address"]) <= 41:
            print(style.RED +"设置地址!" + style.RESET)
            raise SystemExit
        if len(keys["metamask_private_key"]) <= 42:
            print(style.RED +"设置私钥"+ style.RESET)
            raise SystemExit
        return keys["metamask_address"], keys["metamask_private_key"]

    # 滑点
    def setupSlippage(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        return keys['Slippage']

    # 获取合约小数点
    def get_token_decimals(self):
        return self.token_contract.functions.decimals().call()

    # 令牌区块
    def getBlockHigh(self):
        return self.w3.eth.block_number

    def setup_token(self):
        with open("./abis/bep20_abi_token.json") as f:
            contract_abi = json.load(f)
        token_contract = self.w3.eth.contract(address=self.token_address, abi=contract_abi)
        return token_contract

    # 获取账号余额
    def getBnbBalance(self):
        return self.w3.eth.getBalance(self.address)/ (10**18)

    # 获取代币余额
    def get_token_balance(self):
        return self.token_contract.functions.balanceOf(self.address).call() / (10 ** self.token_contract.functions.decimals().call())

    # 获取代币余额
    def get_token_balance_by_token(self, token):
        with open("./abis/bep20_abi_token.json") as f:
            contract_abi = json.load(f)
        ta = Web3.toChecksumAddress(token)
        token_contract = self.w3.eth.contract(address=ta, abi=contract_abi)

        decimals = token_contract.functions.decimals().call()

        # 钱包地址
        o = token_contract.functions.balanceOf(self.address).call()
        tokenBalance = o / (10 ** decimals)
        print(style.GREEN + "token: " + token + " 余额:" + str(tokenBalance) + style.RESET)
        return tokenBalance


    # 计算 gas费
    def estimateGas(self, txn):
        gas = self.w3.eth.estimateGas({
                    "from": txn['from'],
                    "to": txn['to'],
                    "value": txn['value'],
                    "data": txn['data']})
        gas = gas + (gas / 10) # Adding 1/10 from gas to gas!
        maxGasBNB = Web3.fromWei(gas * self.gas_price, "ether")
        print(style.GREEN + "\n最高交易成本 " + str(maxGasBNB) + " BNB" + style.RESET)

        if maxGasBNB > self.MaxGasInBNB:
            print(style.RED +"\nTx 费用超出您的设置，退出")
            raise SystemExit
        return gas

    # 购买
    def buy_token(self):
        with open("./abis/bep20_abi_token.json") as f:
            contract_abi = json.load(f)
        token_contract = self.w3.eth.contract(address=pancake_router, abi=contract_abi)

        # bnb
        bnb = Web3.toChecksumAddress("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")
        toToken = Web3.toChecksumAddress(self.token)

        quantity = Decimal(0.01) * (10 ** 18)

        txn = token_contract.functions.swapExactETHForTokens(
            0,
            [bnb, toToken],
            self.address,
            (int(time.time()) + 10000)
        ).buildTransaction({
            'from': self.address,
            'value': int(quantity),  # This is the Token(BNB) amount you want to Swap from
            'gas': 5800000,
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.getTransactionCount(self.address)
        })

        txn.update({'gas': int(self.estimateGas(txn))})
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )

        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        print(style.GREEN + "\nBUY Hash:", txn.hex() + style.RESET)
        txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)

        if txn_receipt["status"] == 1:
            return True, style.GREEN + "\nBUY Transaction Successfull!" + style.RESET
        else:
            return False, style.RED + "\nBUY Transaction Faild!" + style.RESET


    # 是否授权
    def is_approve(self):
        Approve = self.token_contract.functions.allowance(self.address, pancake_router).call()
        Aproved_quantity = self.token_contract.functions.balanceOf(self.address).call()
        if int(Approve) <= int(Aproved_quantity):
            return False
        else:
            return True

    # 授权
    def approve(self):
        if self.is_approve() == False:
            txn = self.token_contract.functions.approve(
                pancake_router,
                115792089237316195423570985008687907853269984665640564039457584007913129639935 # Max Approve
            ).buildTransaction(
                {'from': self.address,
                'gas': 5800000,
                'gasPrice': self.gas_price,
                'nonce': self.w3.eth.getTransactionCount(self.address),
                'value': 0}
                )
            txn.update({ 'gas' : int(self.estimateGas(txn))})
            signed_txn = self.w3.eth.account.sign_transaction(
                txn,
                self.private_key
            )
            txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(style.GREEN + "\n token:" + self.token + "授权 Hash:", txn.hex()+style.RESET)
            txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
            if txn_receipt["status"] == 1: return True,style.GREEN +"\n 授权成功!"+ style.RESET
            else: return False, style.RED +"\n token 授权失败!"+ style.RESET
        else:
            return True, style.GREEN +"\n 已经授权!"+ style.RESET

