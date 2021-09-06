import unittest.mock
from multiprocessing.managers import SyncManager

class TestChatAcceptance:
    def test_message_exchange(self):
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
        client = ChatClient("User 1")
        client.connection = unittest.mock.Mock()
        sent_message = client.send_message("Hello World")

        assert sent_message == "User 1: Hello World"

    def test_client_connection(self):
        client = ChatClient("User 1")

        connection_spy = unittest.mock.MagicMock()
        with unittest.mock.patch.object(client, "_get_connection",
                                        return_value=connection_spy):
            client.send_message("Hello World")
        # spyが期待通りの値を設定されて呼ばれているかテストする
        connection_spy.broadcast.assert_called_with(("User 1: Hello World"))

class ChatClient:
    def __init__(self, nickname):
        self.nickname = nickname
        self._connection = None

    def send_message(self, message):
        sent_message = "{}: {}".format(self.nickname, message)
        self.connection.broadcast(sent_message)
        return sent_message

    @property
    def connection(self):
        if self._connection is None:
            self._connection = self._get_connection()
        return self._connection
    
    @connection.setter
    def connection(self, value):
        if self._connection is not None:
            self._connection.close()
        self._connection = value

    def _get_connection(self):
        return Connection(("localhost", 9090))

class Connection(SyncManager):
    def __init__(self, address):
        self.register("get_messages")
        super().__init__(address=address, authkey=b'mychatsecret')
        self.connect()

    def broadcast(self, message):
        messages = self.get_messages()
        messages.append(message)

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