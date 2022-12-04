class URL:
    """验证是否一登录"""
    OAUTHLOGIN = "https://iaaa.pku.edu.cn/iaaa/oauthlogin.do"
    LOGIN_REDIRECT = "https://portal.pku.edu.cn/portal2017/ssoLogin.do"
    STUDENT_EXEN_APP = "https://portal.pku.edu.cn/portal2017/util/appSysRedir.do?appId=stuCampusExEn"
    SIMSO_LOGIN = "https://simso.pku.edu.cn/ssapi/simsoLogin"
    SAVE_REQUEST = "https://simso.pku.edu.cn/ssapi/stuaffair/epiApply/saveSqxx"
    LOGIN_CHECK = "https://simso.pku.edu.cn/ssapi/stuaffair/epiApply/getJrsqxx"
    REQUEST_STATUS = "https://simso.pku.edu.cn/ssapi/stuaffair/epiApply/getSqzt"
    SUBMIT = "https://simso.pku.edu.cn/ssapi/stuaffair/epiApply/submitSqxx"
    UPLOAD_IMG = "https://simso.pku.edu.cn/ssapi/stuaffair/epiApply/uploadZmcl"
    QUERY_REQUEST = "https://simso.pku.edu.cn/ssapi/stuaffair/epiApply/getSqxxHis?pageNum=1"


class EXEN_TYPE:
    CAMPUS = "园区往返"
    MEDICAL = "就医"
    INTERNSHIP = "实习"
    STUDY = "学业"
