from request.headers import Randomizer, _AddressState
from request.request import _Connection
from cli import CLI
from helpers import CAPTURING, Watchdog, interval
from instance import Operator, _Instance
from worker import AtomicInteger, _Worker

# device == root
# contains instances
#       dispatcher
#       conn pool (optional)
#       ai functions (optional)
#           something like plugin?
#       ops
#           FETCH - downloads data from web
#           OBSERVE - watches data on web
#           PROCESS - processes data from web
#       dynamic start/stop with cmds
# works for one db
# proxy state check on init and randomly

# DEBUG levels
# 0 - Instance problems
# 1 - Dispatcher, OPS problems
# 2 - HTTP, AI funcs problems

def alert(message, prefix):
    print(f"[{prefix.upper()}]: {message}")

watchdog = Watchdog(callback=alert)
watchdog.start()

@watchdog.monitor
def ping(data):
    print("OK")

if __name__ == "__main__":

    # zz does nothing when used like this >> zz filename
    # without any flags

    randomizer = Randomizer()
    randomizer.start()

    with _Connection("rossmann.pl", 443, 3, ssl=True, redirect=True) as conn:
        response = conn.send("/", randomizer.get_headers(), max_redirects=20)
        print(response[:15].decode())

    # cli = CLI()
    # cli.start()