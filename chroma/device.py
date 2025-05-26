from request.headers import Randomizer, _AddressState
from request.request import _Connection
from cli import CLI
from helpers import CAPTURING, Watchdog, interval
from instance import Operator, _Instance
from worker import AtomicInteger, _Worker

# device == root
# contains instances
#       thread pool
#       ops
#       dynamic start/stop with cmds
# works for one db
# proxy state check on init and randomly

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

    RANDOMIZER = Randomizer()
    RANDOMIZER.start()
    print(RANDOMIZER.get_headers())

    with _Connection("example.com", 80, 5) as conn:
        response = conn.send("/")
        print(response.decode()[:100])

    cli = CLI()
    cli.start()