# from sqladmin import ModelView
# from starlette.requests import Request
# from typing import List, Callable, Type
#
#
# def require_roles(allowed_roles: List[str]):
#     def decorator(cls: Type[ModelView]) -> Type[ModelView]:
#         original_is_accessible = getattr(cls, 'is_accessible', None)
#         original_is_visible = getattr(cls, 'is_visible', None)
#
#         def is_accessible(self, request: Request) -> bool:
#             auth_role = request.session.get("session_token")
#             if auth_role in allowed_roles:
#                 return True
#             # If the original class had its own is_accessible, we check it too.
#             if original_is_accessible:
#                 return original_is_accessible(self, request)
#             return False
#
#         def is_visible(self, request: Request) -> bool:
#             return self.is_accessible(request)
#
#         cls.is_accessible = is_accessible
#         cls.is_visible = is_visible
#         cls.allowed_roles = allowed_roles
#
#         return cls
#
#     return decorator
#
#
# # # Using examples
# # @require_roles(["admin", "moderator"])
# # class DraftCategoryTextAdmin(ModelView, model=DraftCategoryTextModel):
# #     # ... the rest of the model code ...
# #     pass
# #
# # @require_roles(["admin"])
# # class SomeOtherModelAdmin(ModelView, model=DirectPredictAdmin):
# #     # ... the rest of the model code ...
# #     pass
