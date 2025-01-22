"""
统一响应格式模块
处理API响应的标准化格式
"""
from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse
from fastapi import status

class ResponseModel:
    """统一响应模型"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        成功响应
        
        参数:
            data: 响应数据
            message: 响应消息
            status_code: HTTP状态码
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "success": True,
                "message": message,
                "data": data
            }
        )
        
    @staticmethod
    def error(
        message: str = "操作失败",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> JSONResponse:
        """
        错误响应
        
        参数:
            message: 错误消息
            status_code: HTTP状态码
            error_code: 错误代码
            details: 错误详情
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "message": message,
                "error_code": error_code,
                "details": details
            }
        )
