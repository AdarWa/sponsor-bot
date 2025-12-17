"""Admin routes for managing users."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import fastapi_users
from .database import get_async_session
from .models import User
from .schemas import UserRead

router = APIRouter(prefix="/api/admin", tags=["admin"])

current_active_superuser = fastapi_users.current_user(active=True, superuser=True)


@router.get("/users", response_model=list[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_active_superuser),
) -> list[User]:
    """Return every user for admin consumption."""

    result = await session.execute(select(User).order_by(User.email))
    return list(result.scalars().all())


@router.post("/users/{user_id}/verify", response_model=UserRead)
async def verify_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_active_superuser),
) -> User:
    """Mark a user as verified."""

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_verified:
        user.is_verified = True
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_active_superuser),
) -> None:
    """Remove a user account."""

    if admin.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account.")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await session.delete(user)
    await session.commit()
