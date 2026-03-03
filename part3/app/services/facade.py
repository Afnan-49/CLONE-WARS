from __future__ import annotations
from app.persistence.repository import SQLAlchemyRepository

from typing import Any, Dict, List, Optional

from app.persistence.UserRepository import UserRepository
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

from app import db
class HBnBFacade:
    def __init__(self):
        self.user_repo = UserRepository()      
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

    # ---------- Users ----------
        
    def create_user(self, user_data: Dict[str, Any]) -> User:
        user = User(
            first_name=user_data.get("first_name") or "",
            last_name=user_data.get("last_name") or "",
            email=user_data.get("email") or "",
            password="temp",
            is_admin=bool(user_data.get("is_admin", False)),
        )

        raw_pw = user_data.get("password") or ""
        user.hash_password(raw_pw)

        user.validate()

        existing = self.user_repo.get_user_by_email(user.email)
        if existing:
            raise ValueError("Email already exists")

        return self.user_repo.add(user)

    def get_user(self, user_id: str) -> Optional[User]:
        return self.user_repo.get(user_id)

    def list_users(self) -> List[User]:
        return self.user_repo.get_all()

    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        user = self.user_repo.get(user_id)
        if not user:
            return None

        if "first_name" in user_data:
            user.first_name = (user_data.get("first_name") or "").strip()
        if "last_name" in user_data:
            user.last_name = (user_data.get("last_name") or "").strip()
        if "email" in user_data:
            user.email = (user_data.get("email") or "").strip()
        if "password" in user_data:
            raw_pw = (user_data.get("password") or "").strip()
            user.hash_password(raw_pw)            
        if "is_admin" in user_data:
            user.is_admin = bool(user_data.get("is_admin"))

        user.validate()
        return self.user_repo.update(user_id, user_data)

    # ---------- Amenities ----------
    def create_amenity(self, data: Dict[str, Any]) -> Amenity:
        name = (data.get("name") or "").strip()
        amenity = Amenity(name=name)
        amenity.validate()

        if self.amenity_repo.get_by_attribute("name", amenity.name):
            raise ValueError("Amenity name already exists")

        return self.amenity_repo.add(amenity)

    def get_amenity(self, amenity_id: str) -> Optional[Amenity]:
        return self.amenity_repo.get(amenity_id)

    def list_amenities(self) -> List[Amenity]:
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id: str, data: Dict[str, Any]) -> Optional[Amenity]:
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None

        if "name" in data:
            amenity.name = (data.get("name") or "").strip()

        amenity.validate()
        db.session.commit()
        return amenity

    # ---------- Places ---------- #
    def create_place(self, data: Dict[str, Any]) -> Place:
        title = (data.get("title") or "").strip()
        description = data.get("description") or ""
        price = data.get("price")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        owner_id = data.get("owner_id")
        amenity_ids = data.get("amenity_ids") or []

        owner = self.user_repo.get(owner_id)
        if not owner:
            raise ValueError("Owner not found")

        amenities: List[Amenity] = []
        for aid in amenity_ids:
            a = self.amenity_repo.get(aid)
            if not a:
                raise ValueError(f"Amenity not found: {aid}")
            amenities.append(a)

        place = Place(
            title=title,
            description=description,
            price=price,
            latitude=latitude,
            longitude=longitude,
            # owner=owner,
            owner_id=owner.id,
            # amenities=amenities,
        )

        # --- أسطر مضافة حديثاً (لإدارة حالة الخصائص الداخلية) ---
        for a in amenities:
            place.add_amenity_id(a.id)

        # --- أسطر مضافة حديثاً (للحقن الديناميكي لمراجع الكائنات) ---
        place.owner = owner
        place.amenities = amenities

        # place.validate()
        # تم حذف السطر أعلاه (Redundancy Elimination): التهيئة في Place تستدعيها تلقائياً.

        return self.place_repo.add(place)
    def get_place(self, place_id: str) -> Optional[Place]:
        return self.place_repo.get(place_id)

    def list_places(self) -> List[Place]:
        return self.place_repo.get_all()

    def update_place(self, place_id: str, data: Dict[str, Any]) -> Optional[Place]:
        place = self.place_repo.get(place_id)
        if not place:
            return None
        
        data = data or {}
        
        if "title" in data:
            place.title = (data.get("title") or "").strip()

        if "description" in data:
            place.description = data.get("description") or ""

        if "price" in data:
            place.price = data.get("price")

        if "latitude" in data:
            place.latitude = data.get("latitude")

        if "longitude" in data:
            place.longitude = data.get("longitude")

        if "owner_id" in data:
            new_owner = self.user_repo.get(data.get("owner_id"))
            if not new_owner:
                raise ValueError("Owner not found")
            place.owner_id = new_owner.id

        place.validate()
        db.session.commit()

        return place        
        

    # ---------- Reviews ----------
    def create_review(self, data: Dict[str, Any]) -> Review:
        text = (data.get("text") or "").strip()
        rating = data.get("rating")
        user_id = data.get("user_id")
        place_id = data.get("place_id")

        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")

        # ✅ أنشئ Review باستخدام IDs (بدل objects)
        review = Review(
            text=text,
            rating=rating,
            user_id=user.id,
            place_id=place.id,
        )

        # (اختياري) حقن مراجع objects إذا تحتاجينها للعرض فقط
        review.user = user
        review.place = place

        review.validate()
        created = self.review_repo.add(review)

        # ✅ اربطي الـ review بالـ place عن طريق IDs بدل objects
        if not hasattr(place, "review_ids") or place.review_ids is None:
            place.review_ids = []
        place.review_ids.append(created.id)
        

        return created
    
    def get_review(self, review_id: str) -> Optional[Review]:
        return self.review_repo.get(review_id)

    def list_reviews(self) -> List[Review]:
        return self.review_repo.get_all()

    def update_review(self, review_id: str, data: Dict[str, Any]) -> Optional[Review]:
        review = self.review_repo.get(review_id)
        if not review:
            return None
        data = data or {}
        if "text" in data:
            review.text = (data.get("text") or "").strip()
        if "rating" in data:
            review.rating = data.get("rating")

        review.validate()
        db.session.commit()
        return review

    
    def list_reviews_by_place(self, place_id: str) -> List[Review]:
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError("Place not found")

        if hasattr(place, "reviews") and place.reviews is not None:
            return place.reviews

        return [r for r in self.review_repo.get_all() if r.place and r.place.id == place_id]

    def delete_review(self, review_id: str) -> bool:
        review = self.review_repo.get(review_id)
        if not review:
            return False

        # نحذف الربط من place.review_ids
        place_id = getattr(review, "place_id", None)
        if place_id:
            place = self.place_repo.get(place_id)
            if place and hasattr(place, "review_ids") and place.review_ids:
                place.review_ids = [
                    rid for rid in place.review_ids if rid != review_id
                ]
                place.save()

        # نحذف من الريبو
        self.review_repo.delete(review_id)
        return True
facade = HBnBFacade()
