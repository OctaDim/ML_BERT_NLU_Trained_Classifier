import uvicorn
from fastapi import FastAPI

from configs.settings import (
    API_HOST, API_PORT)
from fast_api.app_root_url.router_main import router_root_url
from fast_api.app_tests.router_test_categorise import router_test_categorise
from fast_api.app_tests.router_test_load_model import router_test_load_model
from fast_api.app_tests.router_test_save_model import router_test_save_model
from fast_api.app_tests.router_test_train_categorise import (
    router_test_train_categorise)


routers_list = [
    router_root_url,
    router_test_categorise,
    router_test_train_categorise,
    router_test_save_model,
    router_test_load_model,

]


def create_fastapi_application() -> FastAPI:
    fastapi_app = FastAPI()
    for cur_router in routers_list:
        fastapi_app.include_router(router=cur_router, )
    return fastapi_app


def run_uvicorn_fastapi_server():
    uvicorn.run(app=create_fastapi_application(),
                # app="main:create_fastapi_app",  # literal func call is necessary if server reload=True when code changing
                host=API_HOST,
                port=API_PORT,
                # reload=True,
                # factory=True,
                use_colors=True, )
    print("Uvicorn and FastAPI server started [OK]")


if __name__ == "__main__":
    run_uvicorn_fastapi_server()
