import OpenDartReader
import FinanceDataReader as fdr
import time

# open api
# 1e487de141c22b0a3ad73e2d6b9c08689b5b07d9import os

stock_list = fdr.StockListing("KRX").dropna()

def convert_str_to_float(value):
    if type(value) == float:  # NaN의 자료형은 float입니다.
        return value
    elif value == '-':  # '-'로 되어 있으면 0으로 변환합니다.
        return 0
    else:
        return float(value.replace(',', ''))

def extract_info_and_save(dart, path, year, name, code, report_type, report_type_code):
    report = dart.finstate(code, year, report_type_code)
    if report is None:
        pass
    else:
        submission_date = report['rcept_no'].iloc[0][:8]
        report = report[['fs_nm', 'account_nm', 'thstrm_dt', 'thstrm_amount', 'sj_nm']]
        report.rename({"fs_nm": "개별/연결",
                       "account_nm": "계정명",
                       "sj_nm": "재무제표명",
                       "thstrm_dt": "당기일자",
                       "thstrm_amount": "금액"}, axis=1, inplace=True)
        report['금액'] = report['금액'].apply(convert_str_to_float)

        try:
            os.mkdir(path + "/" + name)
        except:
            pass
        report.to_csv(path + "/{}/{}_{}년_{}.csv".format(name, submission_date, year, report_type),
                      index=False, encoding="euc-kr")


path = './'  # 저장할 경로를 설정하세요.
my_api = '1e487de141c22b0a3ad73e2d6b9c08689b5b07d9'  # Open DART API 키를 입력하세요.
dart = OpenDartReader(my_api)
for code, name in stock_list[['Code', 'Name']].values:
    for year in range(2016, 2022):
        for report_type, report_type_code in zip(["1분기보고서", "반기보고서", "3분기보고서", "사업보고서"],
                                                  ["11013", "11012", "11014", "11011"]):
            print(name, year, report_type)
            while True:
                try:
                    extract_info_and_save(dart=dart,
                                          path=path,
                                          year=year,
                                          name=name,
                                          code=code,
                                          report_type=report_type,
                                          report_type_code=report_type_code)
                    time.sleep(0.5)
                    break
                except:
                    time.sleep(1)
