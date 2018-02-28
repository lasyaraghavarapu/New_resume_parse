import xlrd
import pickle
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )


class CompanyReader():
    def __init__(self, xls_data_path, output_path):
        print 'Importing company data...'

    @staticmethod
    def parse_xls(xls_data_path, output_path, savePickle=True, saveTxt=False, saveDB=False):
        data = xlrd.open_workbook(xls_data_path)
        table = data.sheets()[0]
        xls_list = []
        for i in range(1, table.nrows):
            xls_list.append(table.row_values(i)[0])

        if savePickle:
            with open(output_path, 'wb') as fp:
                pickle.dump(xls_list, fp)

        if saveTxt:
            with open(output_path + '.txt', 'wb') as ft:
                for i in xls_list :
                    ft.write(i + '/n')

    @staticmethod
    def add_company(pickle_path, company_name):
        company_list = pickle.load(pickle_path)
        company_list.append(company_name)
        with open(pickle_path, 'wb') as fp:
            pickle.dump(company_list, fp)

    def store_companyinfo_indb(self):
        pass


if __name__ == '__main__':
    CompanyReader.parse_xls('Sub Industry - Cosmetic company lists (138)  11-1-17.xlsx', 'Cosmetic_companies')
    CompanyReader.parse_xls('Sub Industry - Food & Beverage (531) 11-1-17.xlsx', 'Food_Beverage_companies')
    CompanyReader.parse_xls('Sub Industry - Luxury Goods and Jewelry lists {113) 11-1-17.xlsx', 'Luxury_Goods_Jewelry_companies')
    CompanyReader.parse_xls('Sub Industry - Sporting Goods lists  (185) 11-1-17.xlsx', 'Sporting_Goods_companies')
    CompanyReader.parse_xls('Sub  Industry - Consumer electronic company (607) lists 11-1-17.xlsx', 'Consumer_Electronic_companies')
