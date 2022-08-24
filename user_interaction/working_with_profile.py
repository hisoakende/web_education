from typing import Union

from other.utils import get_password_hash
from user_interaction.requesting_data_from_user import get_email, get_password, request_data, get_profile_type, \
    ProfileType
from working_with_models.models import Administrator, Teacher, Student, User

profiles = {ProfileType.student: Student,
            ProfileType.teacher: Teacher,
            ProfileType.administrator: Administrator}


@request_data('Неправильный email или пароль')
def authenticate_user() -> Union[None, User]:
    """Аутентификация пользователя"""

    type_profile = get_profile_type()
    email = get_email()
    password = get_password()
    model_class = profiles[type_profile]
    user = model_class.manager.get(email=email)
    if user and user.password == get_password_hash(password):
        return user


def register_user():
    pass
