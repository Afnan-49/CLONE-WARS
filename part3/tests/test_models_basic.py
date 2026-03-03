# tests/test_models_basic.py
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity


def test_user_creation():
    user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
    assert user.is_admin is False
    assert user.id is not None
    print("User creation test passed!")


def test_place_and_review_relationship():
    owner = User(first_name="Alice", last_name="Smith", email="alice.smith@example.com")
    place = Place(
        title="Cozy Apartment",
        description="A nice place to stay",
        price=100,
        latitude=37.7749,
        longitude=-122.4194,
        owner_id=owner.id,
    )

    review = Review(text="Great stay!", rating=5, place_id=place.id, user_id=owner.id)
    place.add_review_id(review.id)

    assert len(place.review_ids) == 1
    assert place.review_ids[0] == review.id
    print("Place & Review relationship test passed!")


def test_amenity_relationship():
    owner = User(first_name="Mona", last_name="K", email="mona.k@example.com")
    place = Place(
        title="Sea View",
        description=None,
        price=250,
        latitude=24.7136,
        longitude=46.6753,
        owner_id=owner.id,
    )

    wifi = Amenity(name="Wi-Fi")
    parking = Amenity(name="Parking")

    place.add_amenity_id(wifi.id)
    place.add_amenity_id(parking.id)

    assert len(place.amenity_ids) == 2
    print("Amenity relationship test passed!")


if __name__ == "__main__":
    test_user_creation()
    test_place_and_review_relationship()
    test_amenity_relationship()
    print("All basic model tests passed ✅")
