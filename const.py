"""from enum import Enum"""


class DEFAULT_SETTING(object):
    """Entire System Default Setting"""
    DIR_PATH = './input/'
    FILE_FORMAT = '.csv'
    FUNDAMENTAL_DATA_PREFIX = 'fn_'
    TIME_SERIES_DATA_PREFIX = 'ts_'
    INIT_YEAR = 2009
    ENTER_YEAR = INIT_YEAR + 1
    TIME_WINDOW = 5
    BENCHMARK_NAME = 'KODEX 200'


class CALENDAR(object):
    """According to KRX Trading Calendar"""
    FULL_SCOPE = [year for year in range(2009, 2020)]

    OPENING_DATE = {2008: '2008-01-02', 2009: '2009-01-02', 2010: '2010-01-04', 2011: '2011-01-03', 2012: '2012-01-02',
                    2013: '2013-01-02', 2014: '2014-01-02', 2015: '2015-01-02', 2016: '2016-01-04', 2017: '2017-01-02',
                    2018: '2018-01-02', 2019: '2019-01-02'}

    ENTER_DATE = {2009: '2009-04-01', 2010: '2010-04-01', 2011: '2011-04-01', 2012: '2012-04-02', 2013: '2013-04-01',
                  2014: '2014-04-01', 2015: '2015-04-01', 2016: '2016-04-01', 2017: '2017-04-03', 2018: '2018-04-02',
                  2019: '2019-04-01'}

    QUARTERS = [str(year) + q for year in FULL_SCOPE for q in ['03', '06', '09', '12']]


if __name__ == "__main__":
    print(DEFAULT_SETTING.ENTER_YEAR)
    print("change")