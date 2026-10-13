
from datetime import datetime, timezone, timedelta
import platform

class Settings:

    VERSION = '1.0.0'

    # KST = timezone(timedelta(hours=9))
    # print(datetime.now(KST))
    DATE = '2026-10'

    OS = 'Windows_NT x64 ' + platform.uname().version

    TESTS_DISPLAYED = ['공내재하시험',
                       '공내전단시험',
                       '다짐시험',
                       '밀도시험',
                       '사진첩',
                       '시추공영상촬영',
                       '시추주상도',
                       '시험요약페이지',
                       '실내토질시험',
                       '암석삼축압축강도시험',
                       '암석일축압축강도시험',
                       '암석절리면전단시험',
                       '점하중시험',
                       '지반조사위치도',
                       '지층단면도',
                       '직접전단시험',
                       '콘관입시험',
                       '토질삼축압축시험',
                       '토질일축압축시험',
                       '표준압밀시험',
                       '하향식탄성파시험',
                       '현장베인시험',
                       '현장수압시험',
                       '현장투수시험']  
    


    # TESTS_DISPLAYED에서 추출 하고자 하는 시험
    TEST_ACTIVATED = ['시추주상도']

    