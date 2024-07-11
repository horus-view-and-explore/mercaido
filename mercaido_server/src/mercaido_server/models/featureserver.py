from sqlalchemy import JSON
from sqlalchemy.orm import mapped_column, Mapped

from .meta import Base


class FeatureServer(Base):
    __tablename__: str = "feature_servers"
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, default="")
    endpoint: Mapped[str] = mapped_column(unique=False, nullable=False, default=None)
    attributes: Mapped[dict] = mapped_column(
        JSON(), nullable=True, default_factory=lambda: {}
    )
    server_type: Mapped[str] = mapped_column(nullable=False, default="generic")
