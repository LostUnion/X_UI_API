from app.configuration.routes.routes import *
from app.internal.routes import admin

__routes__ = Routes(
    routers=(admin.router, )
)