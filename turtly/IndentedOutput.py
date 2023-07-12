class IndentedOutput:
    _indentation_level = 0

    def __enter__(self):
        IndentedOutput._indentation_level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        IndentedOutput._indentation_level -= 1

    @staticmethod
    def print(message):
        indentation = "    " * IndentedOutput._indentation_level
        print(f"{indentation}{message}")
