import threading
import queue
import pytest

from todo.app import TODOApp

class TestTODOAcceptance:
    @pytest.fixture
    def fake_inputs(self):
        self.inputs = queue.Queue()
        self.outputs = queue.Queue()

        self.fake_output = lambda txt: self.outputs.put(txt)
        self.fake_input = lambda: self.inputs.get()

        self.get_output = lambda: self.outputs.get(timeout=1)
        self.send_input = lambda cmd: self.inputs.put(cmd)


    def test_main(self, fake_inputs):
        app = TODOApp(io=(self.fake_input, self.fake_output))

        app_thread = threading.Thread(target=app.run, daemon=True)
        app_thread.start()

        welcome = self.get_output()
        expect = """
        TODOs:\n
        \n
        \n
        > 
        """
        assert welcome == expect

        # TODOの追加
        self.send_input("add buy milk")
        welcome = self.get_output()
        expect = """
        TODOs:\n
        1. buy milk\n
        \n
        > 
        """
        welcome == expect

        # TODOの追加
        self.send_input("add buy eggs")
        welcome = self.get_output()
        expect = """
        TODOs:\n
        1. buy milk\n
        2. buy eggs\n
        \n
        > 
        """
        welcome == expect

        # TODOの削除
        self.send_input("del 1")
        welcome = self.get_output()
        expect = """
        TODOs:\n
        1. buy milk\n
        \n
        > 
        """
        welcome == expect

        self.send_input("quit")
        app_thread.join(timeout=1)
        assert self.get_output() == "bye!\n"