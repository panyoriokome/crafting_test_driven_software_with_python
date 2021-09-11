import unittest.mock
from multiprocessing.managers import SyncManager, ListProxy

_messages = []
def _srv_get_messages():
    return _messages
class _ChatServerManager(SyncManager):
    pass
_ChatServerManager.register("get_messages",
                            callable=_srv_get_messages,
                            proxytype=ListProxy) 

def new_chat_server():
    return _ChatServerManager(("", 9090), authkey=b'mychatsecret')

class TestChatAcceptance:
    def test_message_exchange(self):
        with new_chat_server(): # Acceptanceのためにサーバを起動するコマンドを追加
            user1 = ChatClient("山田")
            user2 = ChatClient("佐藤")

            user1.send_message("こんにちは")
            messages = user2.fetch_messages()

            assert messages == ["山田: こんにちは"]

class TestChatClient:
    def test_nickname(self):
        client = ChatClient("User 1")

        assert client.nickname == 'User 1'

    def test_send_message(self):
        client = ChatClient("User 1", connection_provider=unittest.mock.Mock())
        sent_message = client.send_message("Hello World")

        assert sent_message == "User 1: Hello World"

    # def test_client_connection(self):
    #     client = ChatClient("User 1")

    #     connection_spy = unittest.mock.MagicMock()
    #     with unittest.mock.patch.object(client, "_get_connection",
    #                                     return_value=connection_spy):
    #         client.send_message("Hello World")
    #     # spyが期待通りの値を設定されて呼ばれているかテストする
    #     connection_spy.broadcast.assert_called_with(("User 1: Hello World"))

    def test_client_connection(self):
        connection_spy = unittest.mock.MagicMock()

        client = ChatClient("User 1", connection_provider=lambda *args:connection_spy)
        client.send_message("Hello World")
        connection_spy.broadcast.assert_called_with(("User 1: Hello World"))

    def test_client_fetch_messages(self):
        connection = unittest.mock.Mock()
        connection.get_messages.return_value = ["message1", "message2"]

        client = ChatClient("User 1", connection_provider=lambda *args:connection)

        starting_messages = client.fetch_messages()
        client.connection.get_messages().append("message3")
        new_messages = client.fetch_messages()

        # 最初に設定した値が返されることを確認
        assert starting_messages == ["message1", "message2"]
        # 次に新しく追加したメッセージだけが返されることを確認
        assert new_messages == ["message3"]


class Connection(SyncManager):
    def __init__(self, address):
        self.register("get_messages", proxytype=ListProxy)
        super().__init__(address=address, authkey=b'mychatsecret')
        self.connect()

    def broadcast(self, message):
        messages = self.get_messages()
        messages.append(message)

class ChatClient:
    def __init__(self, nickname, connection_provider=Connection):
        self.nickname = nickname
        self._connection = None
        self._connection_provider = connection_provider
        self._last_msg_idx = 0

    def send_message(self, message):
        sent_message = "{}: {}".format(self.nickname, message)
        self.connection.broadcast(sent_message)
        return sent_message

    def fetch_messages(self):
        messages = list(self.connection.get_messages())
        new_messages = messages[self._last_msg_idx:]
        self._last_msg_idx = len(messages)
        return new_messages

    @property
    def connection(self):
        if self._connection is None:
            self._connection = self._connection_provider(("localhost", 
                                                          9090))
        return self._connection
    
    # @connection.setter
    # def connection(self, value):
    #     if self._connection is not None:
    #         self._connection.close()
    #     self._connection = value

    # def _get_connection(self):
    #     return Connection(("localhost", 9090))


class _DummyConnection:
    def broadcast(*args, **kwargs):
        pass

class TestConnection:
    def test_broadcast(self):
        """コネクションを確立させてメッセージの送信ができることを確認する
        """
        # unittest.mock.patch.objectを使ってConnectionにパッチを当てる
        with unittest.mock.patch.object(Connection, "connect"):
            c = Connection(('localhost', 9090))

        # Stub。ここではget_messagesで得られる値をMockしている
        with unittest.mock.patch.object(c, "get_messages", return_value=[]):
            c.broadcast("some message")
            assert c.get_messages()[-1] == "some message"

    def test_exchange_with_server(self):
        with unittest.mock.patch(
            "multiprocessing.managers.listener_client",
            new={"pickle": (None, FakeServer())}
        ):
            c1 = Connection(("localhost", 9090))
            c2 = Connection(("localhost", 9090))

            c1.broadcast("connected message")

            assert c2.get_messages()[-1] == "connected message"

class FakeServer:
    def __init__(self):
        self.last_command = None
        self.last_args = None
        self.messages = []

    def __call__(self, *args, **kwargs):
        return self
    
    def send(self, data):
        # Track any command that was sent to the server.
        callid, command, args, kwargs = data
        self.last_command = command
        self.last_args = args

    def recv(self, *args, **kwargs):
        if self.last_command == "dummy":
            return "#RETURN", None
        elif self.last_command == "create":
            return "#RETURN", ("fakeid", tuple())
        elif self.last_command == "append":
            self.messages.append(self.last_args[0])
            return "#RETURN", None
        elif self.last_command == "__getitem__":
            return "#RETURN", self.messages[self.last_args[0]]
        elif self.last_command in ("incref", "decref", 
                                   "accept_connection"):
            return "#RETURN", None
        else:
            return "#ERROR", ValueError("%s - %r" % (
                self.last_command,self.last_args)
            )

    def close(self):
        pass