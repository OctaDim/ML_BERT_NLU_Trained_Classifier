from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse


router_root_url = APIRouter(prefix="", tags=["ROOT"])


@router_root_url.get(path="/")
async def root_url():
    print("Temporary redirected to /docs [OK]")
    return RedirectResponse(url="/docs",
                            status_code=status.HTTP_307_TEMPORARY_REDIRECT)
