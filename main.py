import uvicorn
from fastapi import FastAPI

from configs.settings import API_HOST, API_PORT
from fast_api.app_add_single_category.router_add_single_category import router_bert_add_single_category
from fast_api.app_add_text_category.router_add_text_category import router_bert_add_text_category
from fast_api.app_add_texts_categories_file.router_add_texts_categories_file import router_bert_add_text_category_file
from fast_api.app_bert_get_all_categories.router_bert_get_all_categories import router_bert_get_all_categories
from fast_api.app_bert_load_model.router_bert_load_model import router_bert_load_model
from fast_api.app_bert_save_model.router_bert_save_model import router_bert_save_model
from fast_api.app_bert_train_model.router_bert_train_model import router_bert_train_model
from fast_api.app_predict_text.router_predict_single_text import router_bert_predict_single_text
from fast_api.app_root_url.router_main import router_root_url
from fast_api.app_test_endpoint.router_test_endpoint import router_develop_test_endpoint
from fast_api.app_tests.router_test_categorise import router_test_categorise
from fast_api.app_tests.router_test_load_model import router_test_load_model
from fast_api.app_tests.router_test_save_model import router_test_save_model
from fast_api.app_tests.router_test_train_categorise import router_test_train_categorise
from fast_api.app_train_task_list.router_train_task_list import router_bert_get_train_tasks_list

routers_list = [
    router_root_url,
    router_test_categorise,
    router_test_train_categorise,
    router_test_save_model,
    router_test_load_model,
    router_bert_predict_single_text,
    router_bert_train_model,
    router_bert_save_model,
    router_bert_load_model,
    router_bert_get_all_categories,
    router_bert_add_text_category,
    router_bert_add_text_category_file,
    router_bert_add_single_category,
    router_bert_get_train_tasks_list,

    # Test end-point (debug time)
    router_develop_test_endpoint,

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


def run_redis():
    pass


if __name__ == "__main__":
    run_uvicorn_fastapi_server()
