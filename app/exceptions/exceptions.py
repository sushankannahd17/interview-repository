class AppException(Exception):
    def __init__(self, detail: str, error_code: str, status_code: int = 500):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(detail)


class EntityNotFoundError(AppException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            detail=f"{entity_name} with ID '{entity_id}' not found",
            error_code="ENTITY_NOT_FOUND",
            status_code=404,
        )


class DuplicateEntityError(AppException):
    def __init__(self, detail: str):
        super().__init__(detail=detail, error_code="DUPLICATE_ENTITY", status_code=409)


class ForbiddenError(AppException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(detail=detail, error_code="FORBIDDEN", status_code=403)


class BusinessValidationError(AppException):
    def __init__(self, detail: str):
        super().__init__(
            detail=detail, error_code="BUSINESS_VALIDATION_ERROR", status_code=422
        )
