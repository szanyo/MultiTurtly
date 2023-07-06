from equipments.security.Unique import Unique


class HermesInterpreter:
    def __init__(self):
        self._commands = {}

    def register_command(self, name, handler):
        self._commands[name] = handler

    def execute_command(self, hermes):
        if hermes.command_name in self._commands:
            handler = self._commands[hermes.command_name]
            handler(*hermes.args, **hermes.kwargs)
            return True
        else:
            return False

    def print_help(self):
        print("Available commands:")
        for command in self._commands:
            print(f"- {command}")


class Hermes(Unique):
    def __init__(self, command_name, *args, **kwargs):
        super().__init__()
        self.generate_uuid()
        self.command_name = command_name
        self.args = args
        self.kwargs = kwargs
