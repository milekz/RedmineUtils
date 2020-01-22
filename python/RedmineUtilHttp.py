import os
from os.path import join, dirname
from dotenv import load_dotenv
import urllib.request
import json


# Redmine REST API
# user data tag List


class JsonUserdata(object):
    def __init__(self, name:str, id: int):
        self.NAME = name
        self.ID = id
# Redmine REST API
# project data tag List
# Data Class
class ProjectData(object):
    def __init__(self, identifier: str, id: int ):
        self.PROJECT_IDENTIFIER = identifier
        self.PROJECT_ID = id

# Redmine REST API
# Ticket data tag List

#
# Redmine Http Accsess
#
class RedmineHttp:
    # redmineのプロジェクト一覧を取得
    def __init__(self):

        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        host= os.environ.get("REDMINE_URL") # 環境変数の値をAPに代入
        api_key = os.environ.get("REDMINE_PASSWORD")

        self.POST = []
        self.API_KEY = api_key
        self.HOST = host
        self.HOST_HEADER = {
            'Content-Type': 'application/json',
            'X-Redmine-API-Key': self.API_KEY
        }
        data = '/projects.json'
        request = urllib.request.Request(self.HOST+data, data=None, headers=self.HOST_HEADER)
        with urllib.request.urlopen(request) as response:
            json_data = response.read().decode('utf-8')
            self.PROJECT_DATA = []
            projectdatas = json.loads(json_data)
            for item in projectdatas['projects']:
                data = ProjectData(item['identifier'],item['id'])
                self.PROJECT_DATA.append(data)



    # Redmineのメンバーを取得
    # いまだと全Redmineメンバーをもってきてしまう
    def GetProjectMembers(self, project_id: str ):
        data = '/users.json'
        request = urllib.request.Request(self.HOST+data, data=None, headers=self.HOST_HEADER)
        with urllib.request.urlopen(request) as response:
            json_data = response.read().decode('utf-8')
            user_data = json.loads(json_data)
            self.USER_DATA = []
            for item in user_data['users']:
                self.USER_DATA.append(JsonUserdata(item['login'],item['id']))


    #特定のプロジェクトのチケットを全部取得
    def GetTicket(self, project_id: int ):
        data = '/issues.json?project_id=%d' % project_id
        request = urllib.request.Request(self.HOST+data, data=None, headers=self.HOST_HEADER)
        with urllib.request.urlopen(request) as response:
            page = response.read().decode('utf-8')
            with open('response.json','a') as f:
                f.write(page)

    # user project_str get ticket
    def GetTicketStr(self, identifier: str ):
#        projlist = self.PROJECT_DATA['projects']
#        'identifier' : 最小単位のプロジェクト名
#        'id' :  project id

        project_id = self.PROJECT_DATA[list(map(lambda x:x.PROJECT_IDENTIFIER, self.PROJECT_DATA)).index(identifier)].PROJECT_ID

        # TODO:redmineの project id には0が入らないため
        if not project_id == 0:
            self.GetTicket(project_id)



    #
    # project_id: プロジェクトID
    # subject   :
    #
    def AddTicket(self, project_id: int, tracker_id: int, subject: str, description: str, user_id:int ):
        url = '/issues.json'
        issue={}
        issue[u'project_id'] = project_id
        issue[u'tracker_id'] = tracker_id
        issue[u'subject'] = subject
        issue[u'description'] = description
        issue[u'assigned_to_id'] = user_id
        data = {}
        data[u'issue'] = issue
        self.POST = json.dumps(data).encode('utf-8')

        request=urllib.request.Request(self.HOST+url, data=self.POST, headers=self.HOST_HEADER, method="POST")
        with urllib.request.urlopen(request) as response:
            decodedata = response.read().decode('utf-8')

    #
    # project str
    # ticket_id : 1: bug, 2 ...
    # user str
    # この状態でチケットを設定できるようにする
    def AddTicketStr(self, identifier: str , tracker_id : int, subject: str, description : str, user: str ):
        # TODO : プロジェクトに存在しないユーザーから登録できないようにする
        #      : 登録時に追加情報を設定する
        project_id = self.PROJECT_DATA[list(map(lambda x:x.PROJECT_IDENTIFIER, self.PROJECT_DATA)).index(identifier)].PROJECT_ID
        user_id = self.USER_DATA[list(map(lambda x:x.NAME, self.USER_DATA)).index(user)].ID

        self.AddTicket(project_id, tracker_id, subject, description, user_id )



if __name__ == '__main__':
    # この時にredmine上に存在するプロジェクトリストを取得
    redmine_api = RedmineHttp()
    # 特定のRedmineプロジェクトにおけるメンバーリストを取得
    redmine_api.GetProjectMembers('dcc')
    # プロジェクトのチケット一覧取得
    redmine_api.GetTicketStr('dcc')
    # プロジェクトのチケットを登録する
    redmine_api.AddTicketStr('dcc', 2, u'PYTHONから登録した2',u'チケット内容\n', 'nsugiyama' )


    # 1. 特定のプロジェクトの誰かのチケットを取得する
    # 2. 特定のプロジェクトのredmineチケットを登録する
    # 3. tracker_id = 1:バグ 2:機能 3:....
    # 4. pngとかでスクリーンショットを登録できたらなおいいかもしれない
    # 5. ue4上のレベル
    # 6. vector3 レベルの配置位置
#    redmine_api.AddTicket('dcc', 2, u'チケット内容 \n windows ubuntuはよ' , u'PYTHONから登録した1' , 'nsugiyama' )
