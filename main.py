from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware

from ML_BERT_classifier.init_bert import init_and_start_bert_model
from admin_panel.admin_auth_role import AdminAuthRoleAuthBackend
from admin_panel.admin_draft_category_text import DraftCategoryTextAdmin
from configs.labels_messages import LABELS
from configs.settings import API_HOST, API_PORT, FASTAPI_OPTIONS, ALCHEMY_OPTIONS, FASTAPI_SESSION_KEY
from db_postgres.postgres_conn_async.pgs_async_connection import close_all_db_connections, PgsAsyncConnection
from db_postgres.postgres_init.db_tables_initialization import initialize_db_tables
from fast_api.app_add_single_category.router_add_single_category import router_bert_add_single_category
from fast_api.app_add_text_category.router_add_text_category import router_bert_add_text_category
from fast_api.app_add_texts_categories_file.router_add_texts_categories_file import router_bert_add_text_category_file
from fast_api.app_bert_load_model.router_bert_load_model import router_bert_load_model
from fast_api.app_bert_save_model.router_bert_save_model import router_bert_save_model
from fast_api.app_bert_train_model.router_bert_train_model import router_bert_train_model
from fast_api.app_checkset_model_test.router_checkset_model_test import router_bert_checkset_model_test
from fast_api.app_create_unique_learn_file.router_create_unique_learn_file import router_bert_create_unique_learn_file
from fast_api.app_get_all_categories.router_get_all_categories import router_bert_get_all_categories
from fast_api.app_get_all_categories_texts.router_get_all_categories_texts import router_bert_get_all_categories_texts
from fast_api.app_get_all_checkset_results.router_all_checkset_results import router_bert_all_checksets_results
from fast_api.app_get_all_train_tasks_list.router_all_train_tasks_list import router_bert_get_train_tasks_list
from fast_api.app_get_checkset_result.router_get_checkset_result import router_bert_single_checkset_result
from fast_api.app_get_confusion_matrix.router_get_confusion_matrix import router_bert_get_confusion_matrix
from fast_api.app_last_dataset_name.router_last_dataset_name import router_bert_last_dataset_name
from fast_api.app_predict_text.router_predict_single_text import router_bert_predict_single_text
from fast_api.app_root_url.router_main import router_root_url
from fast_api.app_test_endpoint.router_test_endpoint import router_develop_test_endpoint
from fast_api.app_tests.test_router_categorise import router_test_categorise
from fast_api.app_tests.test_router_load_model import router_test_load_model
from fast_api.app_tests.test_router_save_model import router_test_save_model
from fast_api.app_tests.test_router_train_categorise import router_test_train_categorise

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
    router_bert_get_all_categories_texts,
    router_bert_add_single_category,
    router_bert_add_text_category,
    router_bert_add_text_category_file,
    router_bert_last_dataset_name,
    router_bert_get_train_tasks_list,
    router_bert_checkset_model_test,
    router_bert_all_checksets_results,
    router_bert_single_checkset_result,
    router_bert_get_confusion_matrix,
    router_bert_create_unique_learn_file,

    # Test end-point (debug time)
    router_develop_test_endpoint,
]

admin_panel_views = [
    # DirectPredictAdmin,
    DraftCategoryTextAdmin,
]


def run_redis():
    # TODO: Check Redis is available and start Redis if not
    print("TODO: Check Redis is available and start Redis if not")
    pass


def run_postgres():
    # TODO: Check Postgres is available and start Postgres if not
    print("TODO: Check Postgres is available and start Postgres if not")
    pass


async def lifespan_on_startup():
    print(">>>>>>> FastAPI Lifespan (startup):")
    run_redis()
    run_postgres()
    if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
        await initialize_db_tables()  # Creating postgres db tables
    await init_and_start_bert_model()  # Initializing Bert model


async def lifespan_on_shutdown():
    print(">>>>>>> FastAPI Lifespan (shutdown):")
    await close_all_db_connections()


@asynccontextmanager
async def fast_api_lifespan(app: FastAPI) -> AsyncGenerator:
    await lifespan_on_startup()
    yield  # FastAPI lifespan yield  (Execution fastapi application)
    await lifespan_on_shutdown()


def setup_admin_panel(
        application: FastAPI | Starlette,
        fastapi_session_key: str
) -> Admin:
    authentication_backend = AdminAuthRoleAuthBackend(
        secret_key=fastapi_session_key)
    admin = Admin(
        app=application,
        engine=PgsAsyncConnection().engine,
        authentication_backend=authentication_backend,
        session_maker=None,
        base_url="/admin",
        title=LABELS.ADMIN_PANEL,
        logo_url=None,
        favicon_url=None,
        middlewares=None,
        debug=False,
        templates_dir="admin_panel/custom_templates",  # Custom templates, origin SQLAdmin value = "templates"
    )
    for cur_admin_view in admin_panel_views:
        admin.add_view(cur_admin_view)
    return admin


def create_fastapi_application() -> SessionMiddleware:
    fastapi_app = FastAPI(lifespan=fast_api_lifespan)
    for cur_router in routers_list:
        fastapi_app.include_router(router=cur_router, )

    setup_admin_panel(application=fastapi_app,
                      fastapi_session_key=FASTAPI_SESSION_KEY)

    fastapi_app_with_middleware = SessionMiddleware(
        app=fastapi_app,
        secret_key=FASTAPI_SESSION_KEY,
        session_cookie="admin_session",
        max_age=600,
        path="/",
        same_site="lax",  # "lax", "strict" or "none"
        https_only=False,
        domain=None)

    # return fastapi_app
    return fastapi_app_with_middleware


def run_uvicorn_fastapi_server():
    uvicorn.run(app=create_fastapi_application(),
                # app="main:create_fastapi_app",  # literal func call is necessary if server reload=True when code changing
                host=API_HOST,
                port=API_PORT,
                # reload=True,
                # factory=True,
                log_level=FASTAPI_OPTIONS.LOG_LEVEL,
                use_colors=FASTAPI_OPTIONS.USE_COLORS, )
    print("Uvicorn and FastAPI server started [OK]")


if __name__ == "__main__":
    run_uvicorn_fastapi_server()
