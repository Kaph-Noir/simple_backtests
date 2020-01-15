from numpy import arange
from pandas import cut
import matplotlib.pyplot as plt
from collections import OrderedDict
from workbench.const import DEFAULT_SETTING


class Explorer:
    @staticmethod
    def get_distribution(fn_data: OrderedDict):
        def autolabel(rects):
            """
            Attach a text label above each bar displaying its height
            """
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., 1.0 * height,
                        '%d' % int(height), ha='center', va='bottom')

        for year, annual_data in fn_data.items():
            bins = [i for i in range(10)]
            groups = cut(annual_data.sort_values(), bins)  # pd.cut()
            y = groups.value_counts()
            ind, width = arange(len(y)), 1  # numpy.arange()
            fig, ax = plt.subplots()  # ?
            rects = ax.bar(ind, y, width)
            autolabel(rects)

            ax.set_xticks(ind - width / 2)
            x = bins
            ax.set_xticklabels(x)

            print("{0} All companies: {1}".format(year, y.sum()))
            plt.title("{0} distributions".format(year))
            plt.show()
        #
        #
        # for i in range(DEFAULT_SETTING.TIME_WINDOW):  # 출력 순서 때문 # 연도순
        #     year = init_year + i
        #     bins = [i for i in range(10)]
        #     x = bins
        #     groups = cut(fn_data[year].sort_values(), bins)  # pd.qcut()
        #     y = groups.value_counts()
        #     ind, width = arange(len(y)), 1
        #     fig, ax = plt.subplots()
        #     rects = ax.bar(ind, y, width)
        #     ax.set_xticks(ind - width / 2)
        #     ax.set_xticklabels(x)
        #     autolabel(rects)
        #     print("{0} All companies: {1}".format(year, y.sum()))
        #     plt.title("{0} PSR distributions".format(year))
        #     plt.show()
        #

if __name__ == "__main__":
    pass
    # pbr_data = dict(Explorer.refine_data(pbr_data))
    # Explorer.get_distribution(pbr_data)