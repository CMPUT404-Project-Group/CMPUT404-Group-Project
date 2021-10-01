from . import User_Data, User

class Current_User(User):

    def __init__(self, user_data: User_Data):
        self.user_data = user_data

    def post_comment(self):
        pass

    def send_friend_request(self, user_id: str):
        pass

    def send_follow_request(self, user_id: str):
        pass