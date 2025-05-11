from enum import Enum, auto
from multiprocessing import Process, cpu_count
from typing import ClassVar, List
from helpers import DEBUG
from worker import AtomicInteger, Dispatcher, _Worker

# *************** Exception ***************

class InstanceException(Exception):
    """Raised when there is a problem with Instance"""

# *************** Ops ***************

class Ops(Enum):
    FETCH_PAGE_COUNT = auto(); FETCH_PROD_COUNT = auto();
    FETCH_PROD_URLS = auto(); FETCH_PROD_DATA = auto();
    PROCESS_PROD_DATA = auto(); SAVE_PROD_DATA = auto(); # saving in other thread???

# *************** Operator ***************

class Operator: # operates instances
    def __init__(self) -> None:
        self._instances = []
    def start(self) -> None:
        instance = _Instance(); instance.start(); self._instances.append(instance)
    def _list_command(self, args: List[str]) -> "Command":
        print("Instances: [" + ", ".join(f"*{instance}" if instance.is_alive() else f"{instance}" for instance in self._instances) + "]")
    def _manage_command(self, args: List[str]) -> "Command":
        if len(args) < 2: print("Usage: instance [run/stop/modify] name") # operate instance with subcommands
        match args[0].lower():
            case "run":
                instance = next((instance for instance in self._instances if str(instance).lower() == args[1].lower()), None)
                if instance is None: print("Unknown name. Type 'instances' for available instances")
                instance.start()
            case "stop": pass
            case "modify": pass
            case _: print("Usage: instance [run/stop/modify] name")

# *************** Instance ***************

class _Instance(Process):
    INSTANCE_ID: ClassVar[AtomicInteger] = AtomicInteger()
    def __init__(self) -> None:
        super().__init__(name=f"Instance-{_Instance.INSTANCE_ID.get_and_increment()}", daemon=True)
        self._dispatcher = Dispatcher()
    def start(self) -> None: self._dispatcher.start()
    def stop(self) -> None:
        self._dispatcher.stop() # join threads
        if DEBUG > 0: print(f"Shutting {self.name}..")
    def is_alive(self) -> bool: return True # change later
    def __str__(self) -> str: return self.name

# instance with prod/page data fetch
# instance with prod analyze
# instance with api server

# data
# id-{first letter of type (uppercase)}
#
# priority:
# clearance:
#
# status:
# classification:

# SECURITY OVERRIDE  SYNCING
#
# {PRODUCTS} {NUMBER} LOG TRANSFER
# ------------------------------------------------
# |# UPLOAD COMPLETE ############################| 100%
# ------------------------------------------------

# http errors handle