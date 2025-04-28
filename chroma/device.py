from helpers import Context, ContextVar, DEBUG
from request.headers import Randomizer, _AddressState
from instance import _Instance
from worker import AtomicInteger, _Worker

# device == root
# contains instances
#       thread pool
#       ops
#       dynamic start/stop with cmds
# works for one db
# proxy state check on init and randomly

if __name__ == "__main__":

    RANDOMIZER = Randomizer()
    RANDOMIZER.start()
    print(RANDOMIZER.get_headers())
    proxy = RANDOMIZER.get_proxies()
    print(proxy[1].state.name)
    proxy[1].state = _AddressState.IDLE
    print(RANDOMIZER.get_proxies()[1].state.name)
    # print(RANDOMIZER.get_proxies()[1])

    at = AtomicInteger()
    print(at.get_and_increment())
    print(at.get_and_increment())
    print(at.get_and_increment())

    # inst = _Instance()
    # inst._print()