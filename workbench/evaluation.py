from collections import OrderedDict
from math import ceil
import matplotlib.pyplot as plt
from numpy import arange
from pandas import DataFrame, Series, concat
from workbench.utils import ToolBox
from workbench.const import CALENDAR, DEFAULT_SETTING


class Evaluation(object):
    @staticmethod
    def get_ts_portf_val(ts_price_years: list, buy_list: OrderedDict, strategy_name=DEFAULT_SETTING.BENCHMARK_NAME) -> DataFrame:
        enter_year = ToolBox.get_enter_year(ts_price_years)
        memo = list()
        for i, data in enumerate(ts_price_years):
            year = enter_year + i
            value = (data.loc[:, buy_list[year].index] * buy_list[year]['volume']).sum(axis=1)
            memo.append(value)
            if i > 0:
                memo[i] = memo[i] * memo[i - 1][-1] / memo[i][0]  # Divided by 0 issue-free?
        ts_portf_val = concat(memo)
        ts_portf_val.name = strategy_name
        return ts_portf_val

    @staticmethod
    def get_scaled_val(ts_value):
        if isinstance(ts_value, Series):
            return round(ts_value * 100 / ts_value[0], 2)
        elif isinstance(ts_value, DataFrame):
            return round(ts_value * 100 / ts_value.iloc[0, :], 2)
        else:
            pass

    @staticmethod
    def get_daily_returns(ts_value):
        return ts_value.pct_change(1)
    # log returns


class Performance(object):
    __slots__ = ['ts_values']

    def __init__(self, *ts_values: Series):
        self.ts_values = ts_values

    def __call__(self):
        pass

    def __repr__(self):
        return f"{self.__name__}"

    def get_returns_plots(self):
        X = list(self.ts_values)[0].index  # Fix
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
            time_window = len(ToolBox.get_entire_years(ts_value))
            cagr = (ts_value[-1] / ts_value[0]) ** (1 / time_window) - 1
            print(f"{ts_value.name} CAGR: {round(cagr * 100, 2)} %")

    def get_annual_returns(self):
        for ts_value in self.ts_values:
            annual_returns = dict()
            years = ToolBox.get_entire_years(ts_value)
            for year in years:
                ts_ret = ts_value.loc[CALENDAR.ENTER_DATE[year]:CALENDAR.ENTER_DATE[year + 1]]
                annual_return = (ts_ret[-1] - ts_ret[0]) / ts_ret[0]
                annual_returns[year] = round(annual_return * 100, 2)
            res = DataFrame(annual_returns, index=[ts_value.name])
            print(res)

    def get_sharpe_ratio(self, rf):  # Needed to fix?
        for ts_value in self.ts_values:
            daily_returns = Evaluation.get_daily_returns(ts_value) - rf
            sharpe_ratio = (252 ** 0.5) * daily_returns.mean() / daily_returns.std()
            print(f"Portfolio: {ts_value.name}")
            print(f"Sharpe Ratio: {sharpe_ratio}\n")

    @staticmethod
    def get_information_ratio(ts_value, ts_benchmark):  # Needed to fix?
        daily_returns = Evaluation.get_daily_returns(ts_value - ts_benchmark)
        information_ratio = (252 ** 0.5) * daily_returns.mean() / daily_returns.std()
        print(f"Portfolio: {ts_value.name}")
        print(f"Information Ratio: {information_ratio}\n")

    def get_hit_ratio(self):
        for ts_value in self.ts_values:
            daily_rets = ts_value.pct_change(1)
            print(f"Portfolio: {ts_value.name}")
            print(f"Win days: {round((daily_rets > 0).sum() * 100 / len(ts_value), 2)} %")
            print(f"Lose days: {round((daily_rets < 0).sum() * 100 / len(ts_value), 2)} %\n")

    def get_hit_ratio_strict(self, rf):
        for ts_value in self.ts_values:
            daily_rets = ts_value.pct_change(1) - rf
            print(f"Portfolio: {ts_value.name}")
            print(f"Win days: {round((daily_rets > 0).sum() * 100 / len(ts_value), 2)} %")
            print(f"Lose days: {round((daily_rets < 0).sum() * 100 / len(ts_value), 2)} %\n")

    @staticmethod
    def get_mdd(ts_value):
        peak = ts_value[0]
        drawdowns = dict()
        for yesterday, today, date in zip(ts_value.shift(1), ts_value, ts_value.index):
            if peak <= today:
                peak, dd = today, 0
            elif yesterday > today:
                dd = 100 * (peak - today) / peak
                drawdowns[dd] = (ts_value[ts_value == peak].index[0], date)
        return OrderedDict(
            sorted(drawdowns.items(), key=lambda x: x[0], reverse=True))  # drawdowns.popitem(last=False)

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
    """
    @staticmethod
    def get_individual_ts_val(ts_price_years: list, buy_list: OrderedDict) -> None:
        styles = ['r-', 'y-', 'm-', 'g-', 'b-', 'r-.', 'y-.', 'm-.', 'g-.', 'b-.']  # 'w-'
        for ts_price, (year, annual_list) in zip(ts_price_years, buy_list.items()):
            print(f"{year}")
            for ticker in buy_list[year].index:
                pnl = (ts_price.loc[:, ticker] * buy_list[year].loc[ticker, 'volume'])
                X = pnl.index
                plt.plot(X, pnl, styles[year % len(buy_list)])
                plt.legend([str(year) + '   ' + ticker], loc='upper left')
                plt.show()
    """

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


    """
    # Rank 변경 시 Sharpe ratio
    @staticmethod
    def get_sharpe_target_ranks(ts_price, ratio, *ranks):
        for rank in ranks:
            target_rank = dict(FinanceDataLoader.get_targets(ts_price, ratio, bottom=rank))
            buy_list = dict(ts_price_loader.get_buylist(ts_price, target_rank))
            sell_list = dict(ts_price_loader.get_selllist(ts_price, buy_list))
            ts_portf_val = Evaluation.get_portf_val(ts_price, buy_list)
            scaled_portf_rets = Evaluation.get_scaled_rets(ts_portf_val)
        yield Evaluation.get_sharpe_ratio(scaled_portf_rets, daily_cd91)


    # Rank 변경 시 매년 연복리 수익률 - Matrix
    def get_cagr_other_cutoffs(ts_price, ratio, *ranks):
        for _, rank in enumerate(ranks):
            target_rank = dict(FinanceDataLoader.get_targets(ts_price, ratio, bottom=rank))
            buy_list = dict(ts_price_loader.get_buylist(ts_price, target_rank))
            sell_list = dict(ts_price_loader.get_selllist(ts_price, buy_list))
            ts_portf_val = Evaluation.get_portf_val(ts_price, buy_list)
            scaled_portf_rets = Evaluation.get_scaled_rets(ts_portf_val)

            def get_annual_returns(ts_rets):
                annual_returns = dict()
                for i in range(time_span):
                    year = enter_year + i
                    ts_ret = ts_rets.loc[enter_date[year]:enter_date[year + 1]]
                    ret = (ts_ret[-1] - ts_ret[0]) / ts_ret[0]
                    annual_returns[year] = "{0} %".format(round(ret * 100, 2))
                return pd.Series(annual_returns, name="Top {0}".format(rank))
            yield get_annual_returns(scaled_portf_rets)
    """
