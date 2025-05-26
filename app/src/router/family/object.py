from sqlalchemy.orm import Session
from app.src.database.models.family import Family
from app.src.database.models.user import User
from app.src.database.session import session_manager
from typing import List, Tuple
from sqlalchemy import or_


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
                Family.family_user_id,
                User.email,
                User.name,
                User.phone,
                User.last_login,
                User.is_active,
                Family.relationship
            ).join(
                User, User.id == Family.family_user_id
            ).filter(
                Family.user_id == self.authorized_user.id
            )

            # Case 2: Current user is a family member
            query2 = db.query(
                Family.user_id.label('family_user_id'),
                User.email,
                User.name,
                User.phone,
                User.last_login,
                User.is_active,
                Family.relationship
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
                    "family_user_id": result.family_user_id,
                    "email": result.email,
                    "name": result.name,
                    "phone": result.phone,
                    "last_login": result.last_login,
                    "is_active": result.is_active,
                    "relationship": result.relationship
                }
                for result in results
            ]

            return family_members, total_count
