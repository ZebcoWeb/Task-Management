from rest_framework.filters import BaseFilterBackend



class PromotionRequestFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        status = request.query_params.get("status", None)
        role = request.query_params.get("role", None)

        if status:
            queryset = queryset.filter(status=status)
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset