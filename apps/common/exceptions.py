"""
API自定义异常处理模块。
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

logger = logging.getLogger(__name__)


class APIException(Exception):
    """API错误基类异常。"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "API错误"
    
    def __init__(self, message: str = None, errors: dict = None):
        self.message = message or self.default_message
        self.errors = errors
        super().__init__(self.message)


class ValidationException(APIException):
    """验证错误异常。"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "参数验证失败"


class NotFoundException(APIException):
    """资源未找到异常。"""
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "资源不存在"


class ServiceException(APIException):
    """服务层异常。"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "服务处理失败"


class LLMException(APIException):
    """LLM服务异常。"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_message = "AI服务暂时不可用"


def custom_exception_handler(exc, context):
    """
    DRF自定义异常处理器。
    提供统一的错误响应格式。
    """
    # 首先调用REST framework的默认异常处理器
    response = exception_handler(exc, context)
    
    # 记录异常日志
    logger.error(f"Exception: {exc}", exc_info=True)
    
    # 处理自定义异常
    if isinstance(exc, APIException):
        data = {
            "status": "error",
            "message": exc.message
        }
        if exc.errors:
            data["errors"] = exc.errors
        return Response(data, status=exc.status_code)
    
    # 处理Django的Http404
    if isinstance(exc, Http404):
        return Response({
            "status": "error",
            "message": "资源不存在"
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 处理Django验证错误
    if isinstance(exc, DjangoValidationError):
        return Response({
            "status": "error",
            "message": "数据验证失败",
            "errors": exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 如果response为None，则是未处理的异常
    if response is None:
        return Response({
            "status": "error",
            "message": "服务器内部错误",
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 标准化DRF的错误响应格式
    if response.status_code >= 400:
        error_data = {
            "status": "error",
            "message": "请求处理失败"
        }
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                error_data["message"] = str(response.data['detail'])
            else:
                error_data["errors"] = response.data
        elif isinstance(response.data, list):
            error_data["errors"] = response.data
        response.data = error_data
    
    return response
