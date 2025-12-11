"""
标准化API响应工具模块 - 与原版 RecruitmentSystemAPI 格式保持一致。
"""
from typing import Any, Optional
from rest_framework.response import Response
from rest_framework import status


class ApiResponse:
    """统一API响应包装器 - 提供标准化的响应格式。"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "成功",
        status_code: int = status.HTTP_200_OK
    ) -> Response:
        """返回成功响应。"""
        return Response({
            "code": 200,
            "message": message,
            "data": data
        }, status=status_code)
    
    @staticmethod
    def created(data: Any = None, message: str = "创建成功") -> Response:
        """返回创建成功响应。"""
        return Response({
            "code": 201,
            "message": message,
            "data": data
        }, status=status.HTTP_201_CREATED)
    
    @staticmethod
    def accepted(data: Any = None, message: str = "任务已提交") -> Response:
        """返回异步任务接受响应。"""
        return Response({
            "code": 202,
            "message": message,
            "data": data
        }, status=status.HTTP_202_ACCEPTED)
    
    @staticmethod
    def error(
        code: int = status.HTTP_400_BAD_REQUEST,
        message: str = "操作失败",
        data: Any = None
    ) -> Response:
        """返回错误响应。"""
        return Response({
            "code": code,
            "message": message,
            "data": data
        }, status=code)
    
    @staticmethod
    def not_found(message: str = "资源不存在") -> Response:
        """返回未找到响应。"""
        return ApiResponse.error(code=status.HTTP_404_NOT_FOUND, message=message)
    
    @staticmethod
    def validation_error(errors: Any, message: str = "参数验证失败") -> Response:
        """返回验证错误响应。"""
        return ApiResponse.error(code=status.HTTP_400_BAD_REQUEST, message=message, data=errors)
    
    @staticmethod
    def server_error(message: str = "服务器内部错误") -> Response:
        """返回服务器错误响应。"""
        return ApiResponse.error(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=message)
    
    @staticmethod
    def paginated(
        items: list,
        total: int,
        page: int,
        page_size: int,
        message: str = "success"
    ) -> Response:
        """返回分页响应。"""
        return Response({
            "code": 200,
            "message": message,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }, status=status.HTTP_200_OK)


# 向后兼容别名
APIResponse = ApiResponse
