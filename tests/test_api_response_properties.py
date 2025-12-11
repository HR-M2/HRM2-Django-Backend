"""
API响应格式属性测试。

使用 hypothesis 进行属性测试，验证响应格式的一致性。
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from rest_framework import status

from apps.common.response import ApiResponse


# **Feature: api-optimization, Property 3: 成功响应格式一致性**
class TestSuccessResponseFormatConsistency:
    """
    Property 3: 成功响应格式一致性
    
    对于任何返回HTTP 2xx状态码的API响应，响应体应包含 code、message、data 三个字段，
    且 code 等于200。
    
    Validates: Requirements 2.1
    """
    
    @given(
        data=st.one_of(
            st.none(),
            st.text(max_size=50),
            st.integers(),
            st.floats(allow_nan=False),
            st.lists(st.integers(), max_size=5),
            st.dictionaries(st.text(max_size=10), st.integers(), max_size=3),
        ),
        message=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_success_response_has_required_fields(self, data, message):
        """成功响应应包含 code, message, data 三个字段。"""
        response = ApiResponse.success(data=data, message=message)
        
        # 验证响应体结构
        assert 'code' in response.data
        assert 'message' in response.data
        assert 'data' in response.data
        
        # 验证 code 等于 200
        assert response.data['code'] == 200
        
        # 验证 HTTP 状态码为 2xx
        assert 200 <= response.status_code < 300
    
    @given(
        data=st.one_of(
            st.none(),
            st.dictionaries(st.text(max_size=20), st.integers(), max_size=5),
        ),
        message=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_created_response_has_required_fields(self, data, message):
        """创建成功响应应包含 code, message, data 三个字段。"""
        response = ApiResponse.created(data=data, message=message)
        
        assert 'code' in response.data
        assert 'message' in response.data
        assert 'data' in response.data
        assert response.data['code'] == 201
        assert response.status_code == status.HTTP_201_CREATED
    
    @given(
        data=st.one_of(
            st.none(),
            st.dictionaries(st.text(max_size=20), st.text(max_size=50), max_size=5),
        ),
        message=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_accepted_response_has_required_fields(self, data, message):
        """异步任务接受响应应包含 code, message, data 三个字段。"""
        response = ApiResponse.accepted(data=data, message=message)
        
        assert 'code' in response.data
        assert 'message' in response.data
        assert 'data' in response.data
        assert response.data['code'] == 202
        assert response.status_code == status.HTTP_202_ACCEPTED


# **Feature: api-optimization, Property 4: 错误响应格式一致性**
class TestErrorResponseFormatConsistency:
    """
    Property 4: 错误响应格式一致性
    
    对于任何返回HTTP 4xx或5xx状态码的API响应，响应体应包含 code、message、data 三个字段，
    且 code 等于HTTP状态码。
    
    Validates: Requirements 2.2
    """
    
    @given(
        code=st.sampled_from([400, 401, 403, 404, 422, 500, 502, 503]),
        message=st.text(min_size=1, max_size=100),
        data=st.one_of(
            st.none(),
            st.text(max_size=100),
            st.dictionaries(st.text(max_size=20), st.text(max_size=50), max_size=5),
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_error_response_has_required_fields(self, code, message, data):
        """错误响应应包含 code, message, data 三个字段。"""
        response = ApiResponse.error(code=code, message=message, data=data)
        
        # 验证响应体结构
        assert 'code' in response.data
        assert 'message' in response.data
        assert 'data' in response.data
        
        # 验证 code 等于 HTTP 状态码
        assert response.data['code'] == code
        assert response.status_code == code
    
    @given(message=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_not_found_response_format(self, message):
        """404响应应包含正确格式。"""
        response = ApiResponse.not_found(message=message)
        
        assert 'code' in response.data
        assert 'message' in response.data
        assert 'data' in response.data
        assert response.data['code'] == 404
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @given(message=st.text(min_size=1, max_size=100))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_server_error_response_format(self, message):
        """500响应应包含正确格式。"""
        response = ApiResponse.server_error(message=message)
        
        assert 'code' in response.data
        assert 'message' in response.data
        assert 'data' in response.data
        assert response.data['code'] == 500
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @given(
        errors=st.one_of(
            st.dictionaries(st.text(max_size=20), st.lists(st.text(max_size=50), max_size=3), max_size=5),
            st.lists(st.text(max_size=50), max_size=5),
        ),
        message=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_validation_error_response_format(self, errors, message):
        """验证错误响应应包含正确格式。"""
        response = ApiResponse.validation_error(errors=errors, message=message)
        
        assert 'code' in response.data
        assert 'message' in response.data
        assert 'data' in response.data
        assert response.data['code'] == 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# **Feature: api-optimization, Property 5: 分页响应格式一致性**
class TestPaginatedResponseFormatConsistency:
    """
    Property 5: 分页响应格式一致性
    
    对于任何返回分页数据的API响应，data 字段应包含 items、total、page、page_size 四个字段。
    
    Validates: Requirements 2.3
    """
    
    @given(
        items=st.lists(st.dictionaries(st.text(max_size=10), st.integers(), max_size=3), max_size=10),
        total=st.integers(min_value=0, max_value=10000),
        page=st.integers(min_value=1, max_value=100),
        page_size=st.integers(min_value=1, max_value=100),
        message=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_paginated_response_has_required_fields(self, items, total, page, page_size, message):
        """分页响应应包含正确的数据结构。"""
        response = ApiResponse.paginated(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message=message
        )
        
        # 验证顶层结构
        assert 'code' in response.data
        assert 'message' in response.data
        assert 'data' in response.data
        assert response.data['code'] == 200
        
        # 验证分页数据结构
        data = response.data['data']
        assert 'items' in data
        assert 'total' in data
        assert 'page' in data
        assert 'page_size' in data
        
        # 验证值的一致性
        assert data['items'] == items
        assert data['total'] == total
        assert data['page'] == page
        assert data['page_size'] == page_size
