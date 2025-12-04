"""
应用自定义中间件模块。
"""
import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """请求/响应日志记录中间件。"""
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # 记录请求详情（跳过静态文件和管理后台）
            if not request.path.startswith(('/static/', '/admin/', '/__debug__/')):
                log_data = {
                    'method': request.method,
                    'path': request.path,
                    'status': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'ip': self.get_client_ip(request),
                }
                
                if response.status_code >= 400:
                    logger.warning(f"Request: {json.dumps(log_data)}")
                else:
                    logger.info(f"Request: {json.dumps(log_data)}")
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class CORSMiddleware(MiddlewareMixin):
    """简单的CORS中间件（生产环境建议使用django-cors-headers）。"""
    
    def process_response(self, request, response):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
