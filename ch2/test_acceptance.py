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
        client.connection = _DummyConnection()
        sent_message = client.send_message("Hello World")

        assert sent_message == "User 1: Hello World"

class ChatClient:
    def __init__(self, nickname):
        self.nickname = nickname

    def send_message(self, message):
        sent_message = "{}: {}".format(self.nickname, message)
        self.connection.broadcast(message)
        return sent_message

class _DummyConnection:
    def broadcast(*args, **kwargs):
        pass