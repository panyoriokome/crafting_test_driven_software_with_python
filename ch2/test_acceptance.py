class TestChatAcceptance:
    def test_message_exchange(self):
        user1 = ChatClient("山田")
        user2 = chatClient("佐藤")

        user1.send_message("こんにちは")
        messages = user2.fetch_messages()

        assert messages == ["山田: こんにちは"]
