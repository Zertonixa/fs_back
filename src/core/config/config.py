from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
TOML_SETTINGS_PATH = BASE_DIR / "config.toml"
JSON_SETTINGS_PATH = BASE_DIR / "config.json"
ENV_PATH = BASE_DIR / ".env"

PathsSources: list[tuple[Path, type[PydanticBaseSettingsSource]]] = [
    (ENV_PATH, EnvSettingsSource),
    (JSON_SETTINGS_PATH, JsonConfigSettingsSource),
    (TOML_SETTINGS_PATH, TomlConfigSettingsSource),
]


class Database(BaseModel):
    """
    Параметры подключения к PostgreSQL и настройки пула SQLAlchemy-asyncpg.
    """

    # ── Основные реквизиты подключения ──────────────────────────────────────────
    postgres_username: str = Field(default="postgres", description=("Имя пользователя PostgreSQL."))
    postgres_db: str = Field(default="postgres", description=("Название базы/схемы."))
    postgres_port: int = Field(default=5432, description=("Порт, на котором слушает PostgreSQL."))
    postgres_host: str = Field(default="localhost", description=("Хост или IP сервера PostgreSQL."))
    postgres_password: str = Field(
        default="postgres", description=("Пароль указанного пользователя.")
    )
    # ── Логирование ─────────────────────────────────────────────────────────────
    echo: bool = Field(default=False, description=("Включить подробный SQL-лог (`echo=True`)."))
    # ── Параметры пула соединений ───────────────────────────────────────────────
    pool_pre_ping: bool = Field(
        default=True,
        description=(
            "Пингует соединение (`SELECT 1`) перед выдачей из пула, выбрасывая «мертвые» коннекты."
        ),
    )
    pool_recycle: int = Field(
        default=1800,
        description=(
            "Максимальный «возраст» соединения (сек). Старая сессия закрывается и "
            "открывается заново, предотвращая idle-тайм-ауты."
        ),
    )
    pool_use_lifo: bool = Field(
        default=False,
        description=(
            "Использовать LIFO вместо FIFO: последний освободившийся коннект "
            "выдаётся первым, снижая шанс «застоя»."
        ),
    )
    pool_timeout: int = Field(
        default=30,
        description=(
            "Сколько секунд ждать свободный коннект, когда пул исчерпан "
            "(`pool_size + max_overflow`). Затем бросается `TimeoutError`."
        ),
    )
    pool_size: int = Field(default=5, description=("Базовое количество постоянных соединений."))
    max_overflow: int = Field(
        default=10,
        description=(
            "Максимум «временных» соединений сверх `pool_size`, создаваемых при "
            "спайках нагрузки. Эти коннекты закрываются при возврате."
        ),
    )

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_username}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


class JWT(BaseModel):
    secret_key: str = Field(default="secret", description="Your secret key")
    algorithm: str = Field(default="HS256", description="Algorithm to jwt")
    expires: int = Field(default=60 * 60 * 24, description="Time to expire your access_token")


class RedisNotify(BaseModel):
    key_prefix: str = Field(default="app:notify:", description="Префикс ключей данных")
    default_ttl_seconds: int = Field(default=3600, description="Fallback TTL for set()")
    negative_ttl_seconds: int = Field(default=60, description="TTL for negative cache entries")


class WeatherApi(BaseModel):
    weather_api_key: str = Field(default="your_api_key")


class S3(BaseModel):
    endpoint: str = Field(default="http://minio:9000", description="URL эндпоинта MinIO/S3.")
    access_key: str = Field(
        default="supersecretkey", description="Ключ доступа (AWS_ACCESS_KEY_ID)."
    )
    secret_key: str = Field(
        default="supersecretkey", description="Секретный ключ (AWS_SECRET_ACCESS_KEY)."
    )
    bucket: str = Field(default="Example", description="Название бакета для хранения файлов.")
    region: str = Field(
        default="us-east-1",
        description="Регион (для MinIO можно оставить фиктивное значение, например us-east-1).",
    )
    use_ssl: bool = Field(default=False, description="Использовать ли SSL для подключения.")
    public_url: str = Field(default="http://localhost:9000")
    addressing_style: str = Field(
        default="path",
        description="Стиль обращения к бакету (path или virtual). Для MinIO обычно path.",
    )


class Logging(BaseModel):
    """
    Настройки уровня логирования для всего приложения.
    """

    level: str = Field(
        default="INFO",
        description="Уровень логирования (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).",
    )


class App(BaseModel):
    """
    Основные параметры конфигурации приложения.
    """

    # ── Сетевые параметры ──────────────────────────────────────────────────────
    host: str = Field(
        default="0.0.0.0",
        description="Хост, на котором запускается приложение (по умолчанию — на всех интерфейсах).",
    )
    port: int = Field(
        default=8000, description="Порт, на котором приложение слушает входящие соединения."
    )
    # ── Производительность ─────────────────────────────────────────────────────
    workers: int = Field(
        default=1, description="Количество воркеров (процессов), обрабатывающих запросы."
    )
    reload: bool = Field(
        default=False,
        description="Автоматическая перезагрузка сервера при изменении кода (удобно в dev-режиме).",
    )
    debug: bool = Field(
        default=False,
        description=(
            "Включение режима отладки — логирует больше и показывает traceback'и в ответах."
        ),
    )
    # ── Часовой пояс ───────────────────────────────────────────────────────────
    tz_offset_hours: int = Field(
        default=3, description="Смещение по времени в часах от UTC (например, `+3` для Москвы)."
    )
    proxy_headers: bool = Field(
        default=False, description="Включайте при запуске на production сервере"
    )
    forwarded_allow_ips: list = Field(
        default=["*"], description="Включайте при запуске на production сервере"
    )


class Docs(BaseModel):
    """
    Настройки доступа к документации (`/docs`).
    """

    allowed_ips: list[str] = Field(
        default=[], description="Список IP-адресов, которым разрешён доступ к `/docs`."
    )


class Bot(BaseModel):
    bot_token: str = Field(default="token", description="Your secret key")


class Security(BaseModel):
    root_admin_telegram_ids: list[int] = Field(default_factory=list, description="Root admin tg id")


class RedisCommon(BaseModel):
    """
    Базовый класс для конфигураций Redis клиентов.
    """

    scheme: Literal["redis", "rediss"] = Field(
        default="redis", description="redis или rediss (TLS)"
    )
    host: str = Field(default="localhost", description="Хост, на котором запускается Redis.")
    port: int = Field(default=6379, description="Порт, на котором запускается Redis.")
    db: int = Field(default=0, description="Номер базы данных.")
    username: str = Field(default="admin", description="Имя супер-пользователя.")
    password: str = Field(default="password", description="Пароль супер-пользователя.")
    decode_responses: bool = Field(default=True, description="Возвращает `str` вместо `bytes`")
    ssl_cert_reqs: Literal["none", "required"] = Field(
        default="none", description="Политика TLS сертификатов"
    )

    # Pool and timeouts
    max_connections: int = Field(default=50, description="Размер пулла подключений.")
    health_check_interval: int = Field(default=30, description="Задержка между PING'ами (в сек.).")
    socket_timeout: float = Field(
        default=5.0, description="Таймаут операции на чтение/запись (в сек.)."
    )
    socket_connect_timeout: float = Field(default=5.0, description="Таймаут подключения (в сек.).")

    socket_keepalive: bool = Field(default=True, description="включение TCP keepalive")

    @property
    def dsn(self) -> str:
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        elif self.password:
            auth = f":{self.password}@"
        return f"{self.scheme}://{auth}{self.host}:{self.port}/{self.db}"

    @property
    def redis_kwargs(self) -> dict:
        kw = {
            "decode_responses": self.decode_responses,
            "health_check_interval": self.health_check_interval,
            "socket_timeout": self.socket_timeout,
            "socket_connect_timeout": self.socket_connect_timeout,
            "socket_keepalive": self.socket_keepalive,
            "max_connections": self.max_connections,
        }
        # TLS switch
        if self.scheme == "rediss":
            import ssl

            kw["ssl"] = True
            kw["ssl_cert_reqs"] = (
                ssl.CERT_NONE if self.ssl_cert_reqs == "none" else ssl.CERT_REQUIRED
            )
        return kw


class RedisPubSub(RedisCommon):
    """
    Отдельный клиент Redis для броекра/pub-sub клиента.
    Обычно DB 0 или отдельный инстанс
    """

    db: int = Field(default=0)


class RedisCache(RedisCommon):
    """
    Отдельный клиент Redis для кэширования данных.
    Обычно DB 1 или отдельный инстанс.
    """

    db: int = Field(default=1)
    key_prefix: str = Field(default="app:cache:", description="Префикс ключей данных")
    default_ttl_seconds: int = Field(default=3600, description="Fallback TTL for set()")
    # Optional negative caching
    negative_ttl_seconds: int = Field(default=60, description="TTL for negative cache entries")


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=ENV_PATH, toml_file=TOML_SETTINGS_PATH
    )

    app: App = App()
    jwt: JWT = JWT()
    weather: WeatherApi = WeatherApi()
    bot: Bot = Bot()
    security: Security = Security()
    redis_notify: RedisNotify = RedisNotify()
    database: Database = Database()
    logging: Logging = Logging()
    docs: Docs = Docs()
    s3: S3 = S3()
    redis_pubsub: RedisPubSub = RedisPubSub()
    redis_cache: RedisCache = RedisCache()

    @classmethod
    def settings_customise_sources(
        cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings
    ):
        return (
            init_settings,
            JsonConfigSettingsSource(settings_cls),
            TomlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


settings = Config()
