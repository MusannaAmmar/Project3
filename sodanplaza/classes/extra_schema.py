from drf_spectacular.utils import extend_schema, OpenApiParameter


def extra_schema(operation_id, params):
    def decorator(view_func):
        return extend_schema(
            operation_id=operation_id,
            parameters=[
                OpenApiParameter(
                    name=param[1:] if param.startswith('+') else param,
                    description=param[1:] if param.startswith('+') else param,
                    required=not param.startswith('+'),
                    type=str,
                ) for param in params
            ]
        )(view_func)

    return decorator
