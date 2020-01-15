from pandas import DataFrame, Series, concat
from math import ceil
from workbench.const import CALENDAR
from workbench.utils import FileHandler, ToolBox


class Order(object):
    @staticmethod
    def _set_portion(enter_prices, weight):
        pass

    @staticmethod
    def get_buylist(ts_price_years, candidates, cut_off: int, weight='equal'):
        enter_year = ToolBox.get_enter_year(ts_price_years)  # 참고한 재무 데이터가 발생한 해 + 1 (실제 진입하는 해)
        for i, data in enumerate(ts_price_years):
            year = enter_year + i
            tickers = data.iloc[0].dropna()  # 진입 당시 상장 폐지 기업 탈락 목적
            _, targets = ToolBox.get_intersection(tickers, candidates[year - 1])
            targets = targets.head(cut_off)
            data = data.loc[:, targets.index]
            enter_prices = data.loc[CALENDAR.ENTER_DATE[year]]
            try:
                # 동일 비중 시, 각 종목 매수량
                if weight == 'equal':
                    portion_inv = sum(enter_prices) / enter_prices  # divided by 0 issue-free?
                    volume = portion_inv.apply(lambda x: ceil(x))  # 해당 종목 주당 가격이 높아 하나도 못 사는 경우 방지 # 일괄 ceil()로 회피
                    enter_prices.name, volume.name = 'price', 'volume'
                    yield year, concat([enter_prices, volume], axis=1)  # 참고한 재무 데이터가 발생한 해 + 1 (실제 진입하는 해)
                # 비중 조절
                # Score 기준
                elif weight == 'score':
                    pass
                # 시총 기준
                else:
                    pass
            except OverflowError as e:
                print(f"divided by 0 issue occurred: {e}")
                print(f"{year}")
                FileHandler.save_as(enter_prices, name='enter_prices')


    @staticmethod
    def get_selllist(ts_price_years, buylist):
        enter_year = ToolBox.get_enter_year(ts_price_years)  # 참고한 재무 데이터가 발생한 해 + 1 (실제 진입하는 해)
        for i, data in enumerate(ts_price_years):
            year = enter_year + i
            targets = buylist[year]
            ts_target_prices = data.loc[:, targets.index]
            exit_prices = ts_target_prices.iloc[-1]
            exit_prices.name = 'price'
            yield year, concat([exit_prices, targets.loc[:, 'volume']], axis=1)


class Execution(object):
    def send_order(self, buylist: DataFrame) -> DataFrame:
        # volume, loss_cut(), etc.
        try:
            timing = Series()
            buylist.merge(timing, how='right')
        except:
            pass
        else:
            pass