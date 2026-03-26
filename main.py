from fastapi import FastAPI

from tasks import routers as tasks_routers

app = FastAPI()

app.include_router(tasks_routers.router)
