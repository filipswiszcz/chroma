from request.headers import Randomizer
from helpers import Context, ContextVar, DEBUG

if __name__ == "__main__":
    REQUEST = ContextVar("REQUEST", "frodo")

    with Context(REQUEST="sam"):
        print(REQUEST.get())

    print(REQUEST.get())

    RANDOMIZER = Randomizer()
    print(RANDOMIZER.get_headers())