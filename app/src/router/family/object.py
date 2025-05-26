from sqlalchemy.orm import Session
from app.src.database.models.family import Family, EnumRelationship
from app.src.database.models.user import User
from app.src.database.session import session_manager
from typing import List, Tuple
from sqlalchemy import or_
from fastapi import HTTPException
from starlette import status
from enum import Enum


class FamilyObject:
    def __init__(self, authorized_user: User):
        self.authorized_user = authorized_user

    async def get_family_members(self) -> Tuple[List[dict], int]:
        """
        Get all family members for the current user.
        This includes:
        1. Family members where the current user is the main user (user_id)
        2. Family members where the current user is a family member (family_user_id)

        Returns a tuple of (family_members, total_count)
        """
        with session_manager() as db:
            # Query to get family members with their user details
            # Case 1: Current user is the main user
            query1 = db.query(
                Family.user_id,
                Family.family_user_id,
                User.email,
                User.name,
                User.phone,
                User.last_login,
                User.is_active,
                Family.relationship,
                Family.is_verified
            ).join(
                User, User.id == Family.family_user_id
            ).filter(
                Family.user_id == self.authorized_user.id
            )

            # Case 2: Current user is a family member
            query2 = db.query(
                Family.user_id,
                Family.family_user_id,
                User.email,
                User.name,
                User.phone,
                User.last_login,
                User.is_active,
                Family.relationship,
                Family.is_verified
            ).join(
                User, User.id == Family.user_id
            ).filter(
                Family.family_user_id == self.authorized_user.id
            )

            # Combine both queries
            results = query1.union(query2).all()
            total_count = len(results)

            # Format results
            family_members = [
                {
                    "user_id": result.user_id,
                    "family_user_id": result.family_user_id,
                    "email": result.email,
                    "name": result.name,
                    "phone": result.phone,
                    "last_login": result.last_login,
                    "is_active": result.is_active,
                    "relationship": result.relationship,
                    "is_verified": result.is_verified
                }
                for result in results
            ]

            return family_members, total_count

    async def add_family_member(self, email: str, relationship: EnumRelationship) -> dict:
        """
        Add a new family member by email.

        Args:
            email: Email of the user to add as family member
            relationship: Relationship type between the users

        Returns:
            dict: Created family member details

        Raises:
            HTTPException: If user is already in a family or if target user doesn't exist
        """
        with session_manager() as db:
            # Check if target user exists
            target_user = db.query(User).filter(User.email == email).first()
            if not target_user:
                raise FileNotFoundError("User not found")

            # Check if target user is already in any family
            existing_family = db.query(Family).filter(
                or_(
                    Family.user_id == target_user.id,
                    Family.family_user_id == target_user.id
                )
            ).first()

            if existing_family:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already part of a family"
                )

            # Check if current user is already in any family
            current_user_family = db.query(Family).filter(
                or_(
                    Family.user_id == self.authorized_user.id,
                    Family.family_user_id == self.authorized_user.id
                )
            ).first()

            if current_user_family:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are already part of a family"
                )

            # Create new family relationship
            new_family = Family(
                user_id=self.authorized_user.id,
                family_user_id=target_user.id,
                relationship=relationship,
                is_verified=False
            )
            db.add(new_family)
            db.commit()
            db.refresh(new_family)

            return {
                "user_id": self.authorized_user.id,
                "family_user_id": target_user.id,
                "email": target_user.email,
                "name": target_user.name,
                "phone": target_user.phone,
                "last_login": target_user.last_login,
                "is_active": target_user.is_active,
                "relationship": relationship,
                "is_verified": False
            }

    async def verify_family_member(self, family_user_id: int) -> dict:
        """
        Verify a family member relationship.
        This can only be done by the family member (family_user_id) to verify their relationship with the main user.

        Args:
            family_user_id: ID of the family member (must match the logged-in user)

        Returns:
            dict: Updated family member details

        Raises:
            HTTPException: If family relationship not found or if user is not authorized
        """
        with session_manager() as db:
            # Check if the family relationship exists and if the current user is the family member
            family = db.query(Family).filter(
                Family.family_user_id == self.authorized_user.id,
                Family.user_id == family_user_id
            ).first()

            if not family:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Family relationship not found"
                )

            # Update verification status
            family.is_verified = True
            db.commit()
            db.refresh(family)

            # Get user details for response
            user = db.query(User).filter(User.id == family.user_id).first()

            return {
                "user_id": self.authorized_user.id,
                "family_user_id": user.id,
                "email": user.email,
                "name": user.name,
                "phone": user.phone,
                "last_login": user.last_login,
                "is_active": user.is_active,
                "relationship": family.relationship,
                "is_verified": family.is_verified
            }
