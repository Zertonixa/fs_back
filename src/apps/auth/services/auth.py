import hashlib
import hmac
import urllib.parse

from ..repositories.interfaces import IUserRepo
from ..schemas.dataclasses.auth import TgUserPayload


class AuthService:

    def __init__(self, user_repo: IUserRepo, bot_token: str, jwt_issuer):

        self.user_repo = user_repo
        self.bot_token = bot_token
        self.jwt_issuer = jwt_issuer

    async def login_with_telegram(self, init_data_raw: str) -> tuple[str, dict]:

        tg_user = self._verify_init_data_and_extract_user(init_data_raw)

        user = await self.user_repo.upsert_by_telegram(tg_user)

        token = self.jwt_issuer({"sub": str(user.id), "tg": user.telegram_id})

        public_user = {
            "id": str(user.id),
            "telegram_id": user.telegram_id,
            "username": user.username,
        }
        return token, public_user

    def _verify_init_data_and_extract_user(self, init_data: str) -> TgUserPayload:

        parsed = urllib.parse.parse_qsl(init_data, keep_blank_values=True)
        data = dict(parsed)

        received_hash = data.pop("hash", None)
        if not received_hash:
            raise ValueError("Missing hash in initData")

        pairs = [f"{k}={v}" for k, v in sorted(data.items()) if k != "hash"]
        data_check_string = "\n".join(pairs)

        secret_key = hashlib.sha256(self.bot_token.encode("utf-8")).digest()
        computed_hash = hmac.new(
            secret_key, data_check_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        if computed_hash != received_hash:
            raise ValueError("Invalid initData signature")

        import json

        user_raw = data.get("user")
        if not user_raw:
            raise ValueError("Missing 'user' in initData")

        user_json = json.loads(user_raw)
        payload = TgUserPayload(
            telegram_id=int(user_json["id"]),
            username=user_json.get("username"),
        )
        return payload
