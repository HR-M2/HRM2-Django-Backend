"""
API分页工具模块。
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """支持自定义页大小的标准分页类。"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        return Response({
            "status": "success",
            "message": "查询成功",
            "data": {
                "items": data,
                "pagination": {
                    "total": self.page.paginator.count,
                    "page": self.page.number,
                    "page_size": self.get_page_size(self.request),
                    "total_pages": self.page.paginator.num_pages,
                    "has_next": self.page.has_next(),
                    "has_previous": self.page.has_previous()
                }
            }
        })


def paginate_queryset(queryset, request, page_size_default=10, max_page_size=50):
    """
    非DRF视图的简单分页辅助函数。
    
    参数:
        queryset: 需要分页的Django查询集
        request: HTTP请求对象
        page_size_default: 默认每页条目数
        max_page_size: 允许的最大页大小
    
    返回:
        tuple: (分页后的条目, 分页信息)
    """
    page = int(request.GET.get('page', 1))
    page_size = min(int(request.GET.get('page_size', page_size_default)), max_page_size)
    
    total = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    
    items = queryset[start:end]
    
    pagination_info = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
    
    return items, pagination_info
