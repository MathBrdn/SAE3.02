from master import Master
from router import Router

master = Master("127.0.0.1", 4000)

routeur1 = Router("127.0.0.1", 5000)
routeur2 = Router("127.0.0.1", 5001)
routeur3 = Router("127.0.0.1", 5002)

master.add_router_obj(routeur1)
master.add_router_obj(routeur2)
master.add_router_obj(routeur3)