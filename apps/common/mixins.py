"""
视图通用功能混入类模块。
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .exceptions import APIException, NotFoundException

logger = logging.getLogger(__name__)


class BaseAPIViewMixin:
    """API视图通用工具基础混入类。"""
    
    def get_param(self, request, key, default=None, required=False):
        """从请求数据或查询参数中获取参数。"""
        value = request.data.get(key) or request.GET.get(key) or default
        if required and value is None:
            raise APIException(f"缺少必要参数: {key}")
        return value
    
    def get_int_param(self, request, key, default=0, required=False):
        """获取整数类型参数。"""
        value = self.get_param(request, key, default, required)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
    
    def get_object_or_404(self, model_class, **kwargs):
        """获取对象或抛出NotFoundException异常。"""
        try:
            return model_class.objects.get(**kwargs)
        except model_class.DoesNotExist:
            model_name = model_class._meta.verbose_name
            raise NotFoundException(f"{model_name}不存在")


class SafeAPIView(BaseAPIViewMixin, APIView):
    """
    内置异常处理的API视图。
    子类应实现handle_get、handle_post等方法。
    """
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except APIException as e:
            # 使用与原版 RecruitmentSystemAPI 一致的错误格式
            return Response(
                {"error": e.message},
                status=e.status_code
            )
        except Exception as e:
            logger.exception(f"未处理的异常: {e}")
            return Response(
                {"error": "服务器内部错误"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, *args, **kwargs):
        if hasattr(self, 'handle_get'):
            return self.handle_get(request, *args, **kwargs)
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def post(self, request, *args, **kwargs):
        if hasattr(self, 'handle_post'):
            return self.handle_post(request, *args, **kwargs)
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def put(self, request, *args, **kwargs):
        if hasattr(self, 'handle_put'):
            return self.handle_put(request, *args, **kwargs)
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self, request, *args, **kwargs):
        if hasattr(self, 'handle_delete'):
            return self.handle_delete(request, *args, **kwargs)
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
