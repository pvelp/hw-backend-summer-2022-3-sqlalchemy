from hashlib import sha256
import typing

from sqlalchemy import insert, select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)
        await self.create_admin(
            email=app.config.admin.email, password=app.config.admin.password
        )

    async def get_by_email(self, email: str) -> Admin | None:
        async with self.app.database.session() as s:
            query_select_admin = select(AdminModel).where(
                AdminModel.email == email
            )
            result = await s.execute(query_select_admin)
            admin = result.scalar()

            return None if admin is None else admin.get_object()

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session() as s:
            query_create_admin = insert(AdminModel).values(
                email=email,
                password=sha256(password.encode()).hexdigest()
            )
            admin = await s.execute(query_create_admin)
            await s.commit()

        return admin
