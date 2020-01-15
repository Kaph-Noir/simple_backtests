import pandas as pd
from collections import OrderedDict
from workbench.const import DEFAULT_SETTING
from pathlib import Path


class FileHandler(object):
    @staticmethod
    def get_data_file(data_type):
        data_path = Path(DEFAULT_SETTING.DIR_PATH)
        try:
            for name in list(data_path.glob('./**/*')):
                file_name = list(name.parts)[-1]
                if data_type in file_name:
                    file_path = name
                    if 'ts' in name.parts:
                        index_col = 'Date'
                    else:
                        print(file_name)
                        print(file_path)
                        index_col = 'Code'
        except ValueError as e:
            print(f"Error: {e}, Check: Directory path or {data_type}")
        except TypeError as e:
            print(f"Error: {e}, Check: Directory path or {data_type}")
        else:
            return pd.read_csv(file_path, index_col=index_col)

    def get_names_from_codes(self, data, data_type='code_name'):
        """
        To get company names from its ticker code
        :param codes:
        :return:
        """
        codes = data.index
        file_path = self.get_data_file(data_type)
        file = pd.read_csv(file_path, index_col='Code')
        return file.loc[codes]

    @staticmethod
    def save_as(data, name='temp', type_='csv'):
        if isinstance(data, pd.DataFrame):
            if type_ == 'csv':
                return data.to_csv(name + '.' + type_, encoding='utf-8-sig')
            else:  # as pickle
                pass
        if isinstance(data, pd.Series):
            df = pd.DataFrame(data)
            df.index.name = name
            if type_ == 'csv':
                return df.to_csv(name + '.' + type_, encoding='utf-8-sig')
            else:  # as pickle
                # import pickle
                pass



class ToolBox(object):
    @staticmethod
    def get_intersection(s1, s2):  # does not need *args yet
        """
        To get intersection elements of 2 pandas Series indexes
        :param s1:
        :param s2:
        :return:
        """
        s1 = s1.loc[s1.index.intersection(s2.index)]
        s2 = s2.loc[s2.index.intersection(s1.index)]
        return s1, s2

    @staticmethod
    def get_candidates(ts_data, begin):
        ts_data = ts_data.loc[:, ts_data.loc[begin].notna()]  # 진입 당시 비상장 기업 탈락 목적
        return ts_data.fillna(0)  # 구간 도중 상장 폐지되는 경우 NaN 값을 0으로 치환: 생존자 편향 방지

    @staticmethod
    def get_enter_year(ts_data):
        if isinstance(ts_data, list):  # input: list
            enter_year = int(ts_data[0].index[0].strftime("%Y"))
        elif isinstance(ts_data, pd.Series):  # input: Series
            enter_year = int(ts_data.index[0].strftime("%Y"))
        return enter_year

    # @staticmethod
    # def get_init_year(fn_data):
    #     if isinstance(fn_data, OrderedDict):
    #         return list(fn_data.keys())[0]

    @staticmethod
    def get_entire_years(data):
        if isinstance(data, pd.Series):  # ts_data
            return [int(i) for i in sorted(set(data.index.strftime("%Y")))][:-1]
        elif isinstance(data, list):  # ts_data
            return [int(annual_data.index[0].strftime("%Y")) for _, annual_data in enumerate(data)][:-1]
        elif isinstance(data, OrderedDict):  # fn_data
            return sorted([year for year in data.keys()])
