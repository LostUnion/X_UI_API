from fastapi import APIRouter
from utils.module_xui.xui_manage import X_UI
from config import Config
from logger_settings import logger_fastapi as log

router = APIRouter(
    prefix='/api/v1'
)

@router.get('/hello')
def user_hello():
    conn = X_UI(
        x_ui_login=Config.X_UI_LOGIN,
        x_ui_password=Config.X_UI_PASSWORD,
        x_ui_link=Config.X_UI_LINK
    )

    if conn:
        log.info("Успешное подключение к X-UI")
        return {
            'Status': 200
        }
    
    else:
        log.error("Не успешное подключение к X-UI")
        return {
            'Status': 401
        }
    