from enum import IntEnum

class UserType(IntEnum):
  STAFF = 1
  STUDENT = 2
  
  @classmethod
  def choices(cls):
    return [(key.value, key.name) for key in cls]