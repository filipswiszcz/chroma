from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Callable
from helpers import DEBUG
from instance import Operator
from worker import _Worker

# *************** Command ***************

class Command(ABC):
    @abstractmethod
    def execute(self, args: List[str]) -> None: pass

class _GenericCommand(Command):
    def __init__(self, command: Callable = None) -> None:
        self.command = command
    def execute(self, args: List[str]) -> None:
        self.command(args)

# *************** Console ***************

class CLI:
    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}
        self._operator = Operator()
        self.__builtin_commands()
        self._running = True
    def __builtin_commands(self) -> None:
        self._commands["help"], self._commands["exit"] = _GenericCommand(self.__help_command), _GenericCommand(self.__exit_command)
        self._commands["instances"], self._commands["instance"] = _GenericCommand(self._operator._list_command), _GenericCommand(self._operator._manage_command)
    def start(self) -> None:
        self._operator.start()
        while self._running:
            try:
                text = input("> ")
                parts = text.strip().split()
                if not parts: continue
                command, *args = parts
                self.execute_command(command, args)
            except KeyboardInterrupt: print("\nUse 'exit' to stop")
            except Exception: pass
    def stop(self) -> None: self._running = False
    def register_command(self, name: str, command: Callable) -> None:
        self._commands[name] = command
    def execute_command(self, name: str, args: List[str]) -> None:
        if name in self._commands:
            try: self._commands[name].execute(args)
            except Exception as exc:
                if DEBUG > 0: print(f"Error occurred while executing command: {exc}")
        else: print(f"Unknown command. Type 'help' for available commands")
    def __help_command(self, args: List[str] = None) -> None:
        print("Commands:\n" + "\n".join(f"* {name}" for name in self._commands))
    def __exit_command(self, args: List[str] = None) -> None:
        print("Exiting console.."); self._running = False