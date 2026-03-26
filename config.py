from fastapi_mail import ConnectionConfig

mail_config = ConnectionConfig(
    MAIL_USERNAME="user",
    MAIL_PASSWORD="user",
    MAIL_FROM="noreply@example.com",
    MAIL_PORT=1025,
    MAIL_SERVER="localhost",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    VALIDATE_CERTS=False,
    USE_CREDENTIALS=False,
)