from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Callable
from helpers import DEBUG

# *************** Command ***************

class Command(ABC):
    @abstractmethod
    def execute(self, args: List[str]) -> None: pass

class _HelpCommand(Command):
    def __init__(self, command: Callable = None) -> None:
        self.command = command
    def execute(self, args: List[str]) -> None:
        self.command(args)

class _ExitCommand(Command):
    def __init__(self, command: Callable = None) -> None:
        self.command = command
    def execute(self, args: List[str]) -> None:
        self.command(args)

# *************** Console ***************

class CLI:
    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}
        self.__builtin_commands()
        self.shutdown = False
    def __builtin_commands(self) -> None:
        self._commands["help"], self._commands["exit"] = _HelpCommand(self.__help_command), _ExitCommand(self.__exit_command)
    def start(self) -> None:
        while not self.shutdown:
            try:
                text = input("> ")
                parts = text.strip().split()
                if not parts: continue
                command, *args = parts
                self.execute_command(command, args)
            except KeyboardInterrupt: print("\nUse 'exit' to stop")
            except Exception: pass
    def stop(self) -> None: self.shutdown = True
    def register_command(self, name: str, command: Callable) -> None:
        self._commands[name] = command
    def execute_command(self, name: str, args: List[str]) -> None:
        if name in self._commands:
            try: self._commands[name].execute(args)
            except Exception as exc:
                if DEBUG > 0: print(f"Error occurred while executing command. {exc}")
        else: print(f"Unknown command. Type 'help' for available commands")
    def __help_command(self, args: List[str] = None) -> None:
        print("Commands:\n" + "\n".join(f"* {name}" for name in self._commands))
    def __exit_command(self, args: List[str] = None) -> None:
        print("Exiting console.."); self.shutdown = True