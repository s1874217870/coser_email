"""
错误处理中间件
处理全局异常和错误响应
"""
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.response import ResponseModel
from typing import Union
import traceback

async def error_handler(
    request: Request,
    exc: Exception
) -> Union[JSONResponse, None]:
    """
    全局错误处理器
    
    参数:
        request: 请求对象
        exc: 异常对象
    """
    # 处理HTTP异常
    if isinstance(exc, HTTPException):
        return ResponseModel.error(
            message=exc.detail,
            status_code=exc.status_code
        )
        
    # 处理验证错误
    if isinstance(exc, RequestValidationError):
        return ResponseModel.error(
            message="请求参数验证失败",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=exc.errors()
        )
        
    # 处理其他异常
    return ResponseModel.error(
        message="服务器内部错误",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_ERROR"
    )
