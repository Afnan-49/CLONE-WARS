from abc import ABC, abstractmethod
from app import db


class Repository(ABC):

    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}

    def add(self, obj):
        self._storage[obj.id] = obj
        return obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if not obj:
            return None
        obj.update(data)
        return obj

    def delete(self, obj_id):
        return self._storage.pop(obj_id, None) is not None

    def get_by_attribute(self, attr_name, attr_value):
        return next(
            (
                obj for obj in self._storage.values()
                if getattr(obj, attr_name, None) == attr_value
            ),
            None
        )
class SQLAlchemyRepository(Repository):
    """
    SQLAlchemy implementation of the Repository pattern.
    Works with a given SQLAlchemy model (db.Model).
    """

    def __init__(self, model):
        self.model = model

    def add(self, obj):
        db.session.add(obj)
        db.session.commit()
        return obj

    def get(self, obj_id):
        return db.session.get(self.model, obj_id)

    def get_all(self):
        return self.model.query.all()

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if not obj:
            return None

        for key, value in (data or {}).items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        db.session.commit()
        return obj

    def delete(self, obj_id):
        obj = self.get(obj_id)
        if not obj:
            return False

        db.session.delete(obj)
        db.session.commit()
        return True

    def get_by_attribute(self, attr_name, attr_value):
        if not hasattr(self.model, attr_name):
            return None
        return self.model.query.filter(getattr(self.model, attr_name) == attr_value).first()
