from abc import abstractmethod


# check func is async
# co_flags = func.__code__.co_flags
# Check if 'func' is a coroutine function.
# (0x180 == CO_COROUTINE | CO_ITERABLE_COROUTINE)
# if co_flags & 0x180:
#     return func

class AgentStarter:

    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    async def stop(self):
        ...


class ApiStarter:

    def __init__(self, root: str):
        self.root = root
        self.action_url = []

    def path(self, uri: str):
        self.action_url.append(self.root + uri)

    def filter(self, api):
        url_routes = {route.path: route for route in api.routes}
        for url, route in url_routes.items():
            if url not in self.action_url:
                api.routes.remove(route)
