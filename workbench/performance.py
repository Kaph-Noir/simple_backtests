from math import ceil
from numpy import arange
from pandas import DataFrame, Series, concat
from collections import OrderedDict
import matplotlib.pyplot as plt
from workbench.utils import ToolBox
from workbench.const import CALENDAR
from workbench.evaluation import Evaluation


class Performance(object):
    def __init__(self, *ts_values: Series):
        self.ts_values = ts_values

    def __call__(self):
        pass

    def __repr__(self):
        return f"{self.__name__}"

    def get_returns_plots(self):
        X = list(self.ts_values)[0].index
        legend = list()
        for ts_value in self.ts_values:
            plt.plot(X, ts_value)
            legend.append(ts_value.name)
        plt.xlabel('Time')
        plt.ylabel('Returns')
        plt.legend(legend, loc='upper left')
        plt.show()

    def get_cagr(self):
        for ts_value in self.ts_values:
            time_window = len(set(ts_value.index.strftime("%Y"))) - 1  # is there any better way?
            cagr = (ts_value[-1] / ts_value[0]) ** (1 / time_window) - 1
            print(f"{ts_value.name} CAGR: {round(cagr * 100, 2)} %")

    def get_annual_returns(self):
        for ts_value in self.ts_values:
            annual_returns = dict()
            years = ToolBox.get_entire_years(ts_value)
            for year in years:
                ts_ret = ts_value.loc[CALENDAR.ENTER_DATE[year]:CALENDAR.ENTER_DATE[year + 1]]
                annual_return = (ts_ret[-1] - ts_ret[0]) / ts_ret[0]
                annual_returns[year] = f"{ts_value.name}: {round(annual_return * 100, 2)} %"
            yield DataFrame(annual_returns)

    def get_hit_ratio(self):
        for ts_value in self.ts_values:
            daily_rets = ts_value.pct_change(1)
            print(f"{ts_value.name}\n")
            print(f"Win days: {round((daily_rets > 0).sum() * 100 / len(ts_value), 2)} %\n")
            print(f"Lose days: {round((daily_rets < 0).sum() * 100 / len(ts_value), 2)} %\n")

    def get_hit_ratio_strict(self, rf):
        for ts_value in self.ts_values:
            daily_rets = ts_value.pct_change(1) - rf
            print(f"{ts_value.name}\n")
            print(f"Win days: {round((daily_rets > 0).sum() * 100 / len(ts_value), 2)} %\n")
            print(f"Lose days: {round((daily_rets < 0).sum() * 100 / len(ts_value), 2)} %\n")

    def get_sharpe_ratio(self, rf):  # Needed to fix?
        for ts_value in self.ts_values:
            daily_rets = ts_value.pct_change(1) - rf
            sharpe_ratio = (252 ** 0.5) * daily_rets.mean() / daily_rets.std()
            print(f"{ts_value.name}\n")
            print(f"Sharpe Ratio: {sharpe_ratio}")

    def get_information_ratio(self, ts_benchmark):  # Needed to fix?
        for ts_value in self.ts_values:
            daily_rets = (ts_value - ts_benchmark).pct_change(1)
            information_ratio = (252 ** 0.5) * daily_rets.mean() / daily_rets.std()
            print(f"{ts_value.name}\n")
            print(f"Information Ratio: {information_ratio}")

    @staticmethod
    def get_mdd(ts_value):
        peak = ts_value[0]
        drawdowns = dict()
        for yesterday, today, date in zip(ts_value.shift(1), ts_value, ts_value.index):
            if peak <= today:
                peak, dd = today, 0
            elif yesterday > today:
                dd = (peak - today) / peak
                drawdowns[dd] = (ts_value[ts_value == peak].index[0], date)
        return OrderedDict(sorted(drawdowns.items(), key=lambda x: x[0], reverse=True))  # drawdowns.popitem(last=False)

    @staticmethod
    def get_pnl(buy_list, sell_list):
        for (year, sell), (_, buy) in zip(sell_list.items(), buy_list.items()):
            profits, losses = Series(buy[(buy['price'] < sell['price'])].index), \
                              Series(buy[(buy['price'] > sell['price'])].index)
            print(f"Year: {year}, Profit: {len(profits)}, Loss: {len(losses)}, Sum: {len(profits) + len(losses)}")
            pnl = sell['price'] * sell['volume'] - buy['price'] * buy['volume']
            ind = arange(len(pnl.index))
            plt.xticks(ind, pnl.index, rotation='vertical')
            plt.yticks(arange((pnl.min() // 10_000) * 10_000, ceil(pnl.max() / 10_000) * 10_000,
                              ceil(((pnl.max() - pnl.min()) / 5) / 10_000) * 10_000))
            color = [[0.8, 0., 0.] if val >= 0 else [0., 0., 0.8] for _, val in enumerate(pnl)]
            plt.bar(ind, pnl.values, color=color)
            plt.show()
            profits.name, losses.name = 'profit', 'loss'
            yield year, concat([profits, losses], axis=1, join='outer')

    @staticmethod
    def get_individual_ts_scaled_val(ts_price_years: list, buy_list: OrderedDict) -> None:
        styles = ['r-', 'y-', 'm-', 'g-', 'b-', 'r-.', 'y-.', 'm-.', 'g-.', 'b-.']  # 'w-'
        for ts_price, (year, annual_list) in zip(ts_price_years, buy_list.items()):
            print(f"{year}")
            for ticker in buy_list[year].index:
                ts_value = (ts_price.loc[:, ticker] * buy_list[year].loc[ticker, 'volume'])
                pnl = Evaluation.get_scaled_val(ts_value)
                X = pnl.index
                plt.plot(X, pnl, styles[year % len(buy_list)])
                plt.legend([str(year) + '   ' + ticker], loc='upper left')
                plt.show()

    # @staticmethod
    # def get_individual_ts_val(ts_price_years: list, buy_list: OrderedDict) -> None:
    #     styles = ['r-', 'y-', 'm-', 'g-', 'b-', 'r-.', 'y-.', 'm-.', 'g-.', 'b-.']  # 'w-'
    #     for ts_price, (year, annual_list) in zip(ts_price_years, buy_list.items()):
    #         print(f"{year}")
    #         for ticker in buy_list[year].index:
    #             pnl = (ts_price.loc[:, ticker] * buy_list[year].loc[ticker, 'volume'])
    #             X = pnl.index
    #             plt.plot(X, pnl, styles[year % len(buy_list)])
    #             plt.legend([str(year) + '   ' + ticker], loc='upper left')
    #             plt.show()


    @staticmethod
    def get_specific_ts_price(ts_price, *tickers: str):
        years = ToolBox.get_entire_years(ts_price)
        for ticker in tickers:
            memo = list()
            for i, _ in enumerate(years):
                memo.append(ts_price[i].loc[:, ticker])
            X = concat(memo)
            plt.plot(X, 'w-')
            plt.legend([ticker], loc='upper right')
            plt.show()
            yield X