import PySide6.QtCore as QtCore
from PySide6.QtWidgets import QApplication # Needed for primaryScreen
from src.db.user_queries import verify_user, get_user_details
from enum import Enum
from src.components.async_worker import Worker
from PySide6.QtCore import QThreadPool

# Simple XOR encryption for demonstration purposes
# WARNING: Simple XOR encryption is NOT secure for production environments.
# This is for demonstration purposes only. In a real application, use robust encryption
# methods (e.g., AES) and secure token storage mechanisms (e.g., OS-level credential storage,
# or a secure backend for token validation and refresh).
_ENCRYPTION_KEY = "supersecretkey"

class AuthResult(Enum):
    SUCCESS = 1
    INVALID_CREDENTIALS = 2
    UNAUTHORIZED = 3 # 401
    FORBIDDEN = 4    # 403
    SERVER_ERROR = 5 # 500
    UNKNOWN_ERROR = 6

def _xor_encrypt_decrypt(data, key=_ENCRYPTION_KEY):
    encrypted_data = ""
    for i, char in enumerate(data):
        encrypted_data += chr(ord(char) ^ ord(key[i % len(key)]))
    return encrypted_data

class UserManager(QtCore.QObject):
    _instance = None
    user_logged_in = QtCore.Signal(str, str) # username, role
    user_logged_out = QtCore.Signal()
    login_completed = QtCore.Signal(AuthResult, str, str) # result, username, role (or error message)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize QObject base class only once
            cls._instance._qobject_init_once()
        return cls._instance

    def _qobject_init_once(self):
        super().__init__()
        self.settings = QtCore.QSettings("ProAuto", "App")
        self._current_user = None
        self.intended_destination = None # Initialize intended_destination here
        self.threadpool = QThreadPool.globalInstance()
        self._load_session()

    def __init__(self):
        # __init__ might be called multiple times for a singleton, but QObject init should only happen once
        pass

    def _load_session(self):
        username = self.settings.value("session/username")
        encrypted_token = self.settings.value("session/token")
        session_timestamp = self.settings.value("session/timestamp")

        if username and encrypted_token and session_timestamp:
            # Check for session expiration (e.g., 1 day timeout)
            stored_datetime = QtCore.QDateTime.fromString(session_timestamp, QtCore.Qt.ISODate)
            if stored_datetime.addDays(1) < QtCore.QDateTime.currentDateTime():
                print("Session expired. Clearing session.")
                self.logout()
                return

            token = _xor_encrypt_decrypt(encrypted_token)
            user_details = get_user_details(username)
            if user_details:
                self._current_user = user_details
                self._current_user["token"] = token # Load token
                print(f"Session loaded for user: {username}")
                self.user_logged_in.emit(username, user_details["role"])

    def login(self, username, password, remember_me=False):
        def _login_task(**kwargs): # Accept **kwargs
            # Simulate API delay
            import time
            time.sleep(1.5) # Simulate 1.5 seconds delay

            # Simulate different API error responses
            if username == "401user":
                return AuthResult.UNAUTHORIZED, None
            if username == "403user":
                return AuthResult.FORBIDDEN, None
            if username == "500user":
                return AuthResult.SERVER_ERROR, None

            if verify_user(username, password):
                user_details = get_user_details(username)
                if user_details:
                    # Return user_details on success, don't modify state here
                    return AuthResult.SUCCESS, user_details
            return AuthResult.INVALID_CREDENTIALS, None

        worker = Worker(_login_task)
        # Pass remember_me to the result handler
        worker.signals.result.connect(lambda result: self._login_result_handler(result, username, remember_me))
        worker.signals.error.connect(lambda exctype, value, tb: self._login_error_handler(exctype, value, tb, username))
        worker.signals.finished.connect(lambda: print("Login task finished."))
        self.threadpool.start(worker)

    def _login_error_handler(self, exctype, value, tb, username):
        print(f"Login task error: {exctype.__name__}: {value}")
        import traceback
        print(''.join(traceback.format_exception(exctype, value, tb)))
        self.login_completed.emit(AuthResult.SERVER_ERROR, username, None)

    def _login_result_handler(self, result_tuple, username, remember_me):
        auth_result, data = result_tuple # data is user_details or None

        if auth_result == AuthResult.SUCCESS:
            # All state modifications happen here, on the main thread
            user_details = data
            self._current_user = user_details

            # Mock token generation and rotation
            token_data = self._generate_mock_token_data()
            self._current_user["token"] = token_data["token"]
            self._current_user["token_expires_at"] = token_data["expires_at"]

            if remember_me:
                self.settings.setValue("session/username", username)
                self.settings.setValue("session/token", _xor_encrypt_decrypt(self._current_user["token"]))
                self.settings.setValue("session/token_expires_at", self._current_user["token_expires_at"].toString(QtCore.Qt.ISODate))
                self.settings.setValue("session/timestamp", QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate))
                self.settings.sync()
            else:
                self.settings.remove("session/username")
                self.settings.remove("session/token")
                self.settings.remove("session/token_expires_at")
                self.settings.remove("session/timestamp")
                self.settings.sync()

            # Emit signals from the main thread
            self.user_logged_in.emit(username, user_details["role"])
            self.intended_destination = None
            self.login_completed.emit(auth_result, username, user_details["role"])
        else:
            self.login_completed.emit(auth_result, username, None)

    def logout(self):
        # Only emit the signal if a user was actually logged in.
        was_logged_in = self._current_user is not None

        self._current_user = None
        self.settings.remove("session/username")
        self.settings.remove("session/token") # Remove token on logout
        self.settings.remove("session/token_expires_at")
        self.settings.remove("session/timestamp")
        self.settings.sync()

        if was_logged_in:
            self.user_logged_out.emit()

    def _generate_mock_token_data(self):
        import uuid
        token = str(uuid.uuid4())
        expires_at = QtCore.QDateTime.currentDateTime().addSecs(300) # Token expires in 5 minutes
        return {"token": token, "expires_at": expires_at}

    def _refresh_token(self):
        print("Simulating token refresh...")
        import time
        time.sleep(0.5) # Simulate refresh delay
        token_data = self._generate_mock_token_data()
        self._current_user["token"] = token_data["token"]
        self._current_user["token_expires_at"] = token_data["expires_at"]
        # Update persisted token if remember_me was true
        if self.settings.value("session/username") and self.settings.value("session/token"):
            self.settings.setValue("session/token", _xor_encrypt_decrypt(self._current_user["token"]))
            self.settings.setValue("session/token_expires_at", self._current_user["token_expires_at"].toString(QtCore.Qt.ISODate))
        print("Token refreshed.")
        return True

    def get_current_user(self):
        if self._current_user and self._current_user.get("token_expires_at"):
            if QtCore.QDateTime.currentDateTime() > self._current_user["token_expires_at"]:
                print("Token expired. Attempting refresh...")
                if self._refresh_token():
                    return self._current_user
                else:
                    self.logout()
                    return None
        return self._current_user

    def is_logged_in(self):
        # Also trigger token refresh check when checking login status
        return self.get_current_user() is not None

    def get_user_role(self):
        # Ensure token is valid before returning role
        if self.get_current_user():
            return self._current_user["role"]
        return None

    def get_username(self):
        # Ensure token is valid before returning username
        if self.get_current_user():
            return self._current_user["username"]
        return None

    def save_last_active_page(self, page_name):
        self.settings.setValue("ui/last_active_page", page_name)

    def get_last_active_page(self):
        return self.settings.value("ui/last_active_page", "dashboard") # Default to dashboard
