from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        
        # Add tags
        if not hasattr(schema, 'tags'):
            schema.tags = []
        
        schema.tags.extend([
            {
                "name": "Authentication",
                "description": "User authentication endpoints"
            },
            {
                "name": "Wallet",
                "description": "Wallet management endpoints"
            },
            {
                "name": "Transactions",
                "description": "Transaction management endpoints"
            },
            {
                "name": "Health",
                "description": "Health check endpoints"
            }
        ])
        
        # Add JWT security scheme only (no Basic auth)
        if not hasattr(schema, 'securityDefinitions'):
            schema.securityDefinitions = {}
        
        schema.securityDefinitions['Bearer'] = {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your JWT token in the format: Bearer <token>"
        }
        
        # Set Bearer as the default security requirement
        if not hasattr(schema, 'security'):
            schema.security = []
        
        schema.security.append({"Bearer": []})
        
        return schema


# Swagger schema view with JWT authentication only
schema_view = get_schema_view(
    openapi.Info(
        title="Secure Wallet API",
        default_version='v1',
        description="""
        A secure wallet API with JWT Bearer token authentication, balance management, and transaction history.
        
        ## Authentication
        This API uses JWT Bearer tokens for authentication. To use protected endpoints:
        
        1. Register a new user or login to get access and refresh tokens
        2. Click the "Authorize" button in Swagger UI and enter: `Bearer <your_access_token>`
        3. Use the refresh token to get a new access token when it expires
        
        ## Getting Started
        1. Register a new user using the `/api/v1/auth/register/` endpoint
        2. Login using `/api/v1/auth/login/` to get your JWT tokens
        3. Click "Authorize" and enter your Bearer token
        4. Refresh your token using `/api/v1/auth/refresh/` when needed
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@walletapi.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[JWTAuthentication],
    generator_class=CustomSchemaGenerator,
) 