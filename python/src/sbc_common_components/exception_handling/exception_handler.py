# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Function to handle all exceptions."""
from flask_jwt_oidc import AuthError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException, default_exceptions

RESPONSE_HEADERS = {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}


class ExceptionHandler():
    """Class to handle exceptions."""

    def __init__(self, app=None):
        """Private constructor."""
        if app:
            self.init_app(app)

    def auth_handler(self, error):  # pylint: disable=no-self-use
        """Handle AuthError."""
        return error.error, error.status_code, RESPONSE_HEADERS

    def db_handler(self, error):  # pylint: disable=no-self-use
        """Handle Database error."""
        return {'error': '{}'.format(error.__dict__['code']),
                'message': '{}'.format(str(error.__dict__['orig']))}, error.status_code, RESPONSE_HEADERS

    def std_handler(self, error):  # pylint: disable=no-self-use
        """Handle standard exception."""
        message = dict(messaage=error.message if hasattr(error, 'message') else error.description)
        return message, error.code if isinstance(error, HTTPException) else 500, RESPONSE_HEADERS

    def init_app(self, app):
        """Register common exceptons or errors."""
        self.app = app
        self.register(AuthError, self.auth_handler)
        self.register(HTTPException)
        self.register(SQLAlchemyError, self.db_handler)
        for exception in default_exceptions:
            self.register(self._get_exc_class_and_code(exception))

    def register(self, exception_or_code, handler=None):
        """Register exception with handler."""
        self.app.errorhandler(exception_or_code)(handler or self.std_handler)

    @staticmethod
    def _get_exc_class_and_code(exc_class_or_code):
        """Get the exception class being handled.

        For HTTP status codes or ``HTTPException`` subclasses, return both the exception and status code.

        :param exc_class_or_code: Any exception class, or an HTTP status code as an integer.
        """
        if isinstance(exc_class_or_code, int):
            exc_class = default_exceptions[exc_class_or_code]
        else:
            exc_class = exc_class_or_code

        assert issubclass(exc_class, Exception)

        return exc_class
