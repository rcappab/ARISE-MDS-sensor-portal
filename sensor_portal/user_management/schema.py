from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, extend_schema_view

# ResetPasswordConfirmViewSet
# ResetPasswordRequestTokenViewSet


class Fix1(OpenApiViewExtension):
    target_class = 'django_rest_passwordreset.views.reset_password_request_token'

    def view_replacement(self):

        class Fixed(self.target_class):

            @extend_schema(exclude=True)
            def post(self, request, *args, **kwargs):
                pass

        return Fixed


class Fix2(OpenApiViewExtension):
    target_class = 'django_rest_passwordreset.views.reset_password_confirm'

    def view_replacement(self):

        class Fixed(self.target_class):

            @extend_schema(exclude=True)
            def post(self, request, *args, **kwargs):
                pass

        return Fixed


class Fix3(OpenApiViewExtension):
    target_class = 'django_rest_passwordreset.views.reset_password_validate_token'

    def view_replacement(self):

        class Fixed(self.target_class):

            @extend_schema(exclude=True)
            def post(self, request, *args, **kwargs):
                pass

        return Fixed
