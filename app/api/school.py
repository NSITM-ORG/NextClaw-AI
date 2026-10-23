"""
School route bridge for app/api/school.py.
Delegates to api.routes.school.
"""
from api.routes.school import router, SchoolQueryRequest, SchoolQueryResponse

__all__ = ["router", "SchoolQueryRequest", "SchoolQueryResponse"]
