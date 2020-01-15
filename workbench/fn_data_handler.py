from collections import OrderedDict
from workbench.const import DEFAULT_SETTING, CALENDAR
from workbench.utils import FileHandler, ToolBox


class FundamentalDataLoader(object):
    __slots__ = ['sep', 'month']  # 'sep' means 'separated_by'

    def __init__(self, sep='y'):
        self.sep = sep
        if self.sep == 'y':  # yearly
            self.month = '12'
        elif self.sep == 'h':  # half of the year
            self.month = '06'
        else:  # 'q' means quarterly
            pass

    def get_fn_data(self, data_type, first_year=DEFAULT_SETTING.INIT_YEAR,
                    time_window=DEFAULT_SETTING.TIME_WINDOW, where='bs'):  # 연말 정기 공시만 있는 기업의 경우? e.g. 삼성물산
        fn_file = FileHandler.get_data_file(data_type)
        print(fn_file.columns)
        fn_file = fn_file.loc[:, str(first_year) + '03':str(first_year + time_window) + '03']
        # 진입 당시 상장 폐지 기업 탈락 목적

        fn_file = fn_file.loc[fn_file.loc[:, str(first_year) + self.month].notna()]
        if self.sep == 'y':
            fn_file = fn_file.filter(regex=r'^20[0-1][0-9](12)$', axis=1)
            if where == 'bs':  # bs means Balance Sheet
                for col in fn_file.columns:
                    yield int(col[:4]), fn_file.loc[:, col]
            else:  # for 'is' which means Income Statement or 'cf', Cash Flow
                for i in range(time_window):
                    year = first_year + i
                    # Is below line right?
                    yield year, fn_file.loc[:, str(year) + '03':str(year) + '12'].sum(axis=1, min_count=1)  # for preventing NaN values from replacing 0
        elif self.sep == 'h':
            fn_file = fn_file.filter(regex=r'^20[0-1][0-9](06|12)$', axis=1)
            if where == 'bs':  # bs means Balance Sheet
                for col in fn_file.columns:
                    yield int(col), fn_file.loc[:, col]
            else:  # for 'is' which means Income Statement or 'cf', Cash Flow
                if self.sep == '12':
                    for i in range(time_window):
                        year = first_year + i
                        # Is below line right?
                        yield year, fn_file.loc[:, str(year) + '03':str(year) + '12'].sum(axis=1, min_count=1)  # for preventing NaN values from replacing 0
                else:  # '06'
                    for i in range(time_window):
                        year = first_year + i
                        # Is below line right?
                        yield year, fn_file.loc[:, str(year - 1) + '09':str(year) + '06'].sum(axis=1, min_count=1)  # for preventing NaN values from replacing 0


class FinanceRatio(object):
    @staticmethod
    def get_ratio(ts_data_years, fn_data_years, type_='mean'):
        for i, (year, annual_data) in enumerate(fn_data_years.items()):
            if type_ == 'mean':
                mean = ts_data_years[i].mean()
                capsize = mean.dropna()  # Divided by Zero check
            elif type_ == 'median':
                median = ts_data_years[i].median()
                capsize = median.dropna()
            else:  # 'end_of_the_year' or 'enter_date'  # not yet
                pass
            # for 2 data diff. check
            capsize, annual_data = ToolBox.get_intersection(capsize, annual_data)
            ratio = capsize / annual_data
            yield year, ratio

    @staticmethod
    def get_assets_related_ratio(fn_data, fn_assets):
        for (year, annual_data), (_, annual_assets) in zip(fn_data.items(), fn_assets.items()):
            annual_data = annual_data.dropna()
            annual_assets = annual_assets.dropna()
            # Divided by Zero check
            ratio = (annual_data / annual_assets)
            yield year, ratio.dropna()

    @staticmethod
    def get_return_ratio(fn_earning, fn_data):
        for year, annual_data in fn_data.items():
            annual_earning = fn_earning[year].dropna()
            annual_data = annual_data.dropna()
            # Divided by Zero check
            ratio = (annual_earning / annual_data)
            yield year, ratio


if __name__ == "__main__":
    from workbench.ts_data_handler import TimeSeriesDataLoader
    ts_data_loader = TimeSeriesDataLoader()
    ts_capsize = list(ts_data_loader.get_ts_data('capsize', reference_date=CALENDAR.OPENING_DATE))
    fn_data_loader = FundamentalDataLoader()
    fn_earning = OrderedDict(fn_data_loader.get_fn_data('earning', where='is'))
    fn_ratio = FinanceRatio()
    per = OrderedDict(fn_ratio.get_ratio(ts_capsize, fn_earning))
    ToolBox.save_as(per, name='per')