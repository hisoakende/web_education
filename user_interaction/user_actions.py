from other.utils import get_password_hash
from user_interaction.messages import profile_type_msg, print_obj_with_this_data_msg, save_account_msg, save_obj_msg
from user_interaction.services import *
from user_interaction.services import create_dict_with_user_data, profiles, try_to_insert_obj_to_db
from working_with_models.models import User, SubjectClassTeacher, Grade


def authenticate_user() -> Optional[User]:
    """Аутентификация пользователя"""

    type_profile = get_choice(ProfileType, profile_type_msg)
    email = get_answer('Введите email:')
    password = get_answer('Введите пароль:', getpass)
    if len(password) == 64:
        print_error('Неправильный email или пароль\nПовторите процедуру аутентификации еще раз')
        return
    model_class = profiles[type_profile]
    user = model_class.manager.get(email=email)
    if not user or user.password != get_password_hash(user.second_name + password + user.email):
        print_error('Неправильный email или пароль\nПовторите процедуру аутентификации еще раз')
        return
    return user


def register_user() -> Union[None, User]:
    """Регистрация пользователя"""

    type_profile = get_choice(ProfileType, profile_type_msg)
    model_class = profiles[type_profile]
    data = create_dict_with_user_data(model_class)
    if data['password'] != data['repeated_password']:
        print_error('Введенные пароли не совпадают')
        print_error('Повторите процедуру регистрации еще раз')
        return
    data.pop('repeated_password')
    user = try_to_create_obj(model_class, *data.values())
    if user is None:
        print_error('Повторите процедуру регистрации еще раз')
        return
    data.pop('password')
    print_obj_with_this_data_msg(user)
    save_account_msg()
    user = finish_registration(user)
    if user is None:
        print_error('Повторите процедуру регистрации еще раз')
        return
    return user


def logout() -> None:
    """Выход из аккаунта"""
    State.user = None


def show_grades(student: Optional[User] = None) -> None:
    """Показывает все оценки ученика за текущий период (атрибут 'current_dates' класса State)"""

    if student is None:
        student = State.user
    subjects = get_objs_from_sct(SubjectClassTeacher.manager.filter(school_class=student.school_class), 'subject')
    raw_table = get_empty_table_dict(subjects)
    grades = Grade.manager.filter(student=student)
    fill_raw_table_with_grades(raw_table, grades, 'subject')
    pretty_table = get_pretty_table()
    prepare_pretty_table_for_grades(pretty_table, subjects)
    fill_pretty_table_with_grades(raw_table, pretty_table)
    print(pretty_table)


def get_my_teachers() -> None:
    """Показывает всех учителей, которые ведут предметы у конкректного ученика"""

    pretty_table = get_pretty_table()
    prepare_pretty_table_for_tchs_list(pretty_table)
    student_class = State.user.school_class
    teachers_subjects = SubjectClassTeacher.manager.filter(school_class=student_class)
    fill_pretty_table_with_tchs(pretty_table, teachers_subjects)
    print(pretty_table)


def rate_students_by_teacher() -> None:
    """Позволяет учителю выставить оценки своим ученикам"""

    try:
        school_class, subject = get_data_to_rate_students(State.user)
    except NoSubjectsTaughtByTheTeacher:
        print_error('Вы не ведете ни одного предмета!')
    else:
        process_student_grading(school_class, subject)


def rate_students_by_administrator() -> None:
    """Позволяет администратору выставить оценки любому ученику в школе"""

    school_class, subject = get_data_to_rate_students()
    process_student_grading(school_class, subject)


def print_school_class_grades(school_class: Class) -> None:
    """Печатает успеваемость класса без возможности редактировать оценки"""

    subjects = get_objs_from_sct(SubjectClassTeacher.manager.filter(school_class=school_class), 'subject')
    subject = get_obj_from_user(subjects, 'предмет')
    print_class_grades_table(school_class, subject)


def print_grades_of_student(school_class: Class) -> None:
    """Печатает успеваемость одного ученика без возможности редактировать оценки"""

    students = sorted(Student.manager.filter(school_class=school_class), key=lambda x: x.second_name)
    student = get_obj_from_user(students, 'ученика')
    print(f'Успеваемость {student}:')
    show_grades(student)


def create_obj_by_admin(model_class: model_classes_for_admin_work) -> None:
    """Позволяет администратору добавить объект в систему"""

    if model_class is Period:
        print('Дата ставится в формате: (день/месяц/год)')
    try:
        values = get_values_to_create_obj_by_admin(model_class)
    except InvalidData:
        print_error('Неккоректные данные!')
        return
    if model_class is Period and values[1] <= values[0]:
        print_error('Конечная дата не может раньше или совпадать с текущей.\n')
        return
    obj = try_to_create_obj(model_class, *values)
    if obj is None:
        print_error('Неуспешно!')
        return
    print_obj_with_this_data_msg(obj)
    save_obj_msg()
    if (isinstance(obj, (Teacher, Student)) and finish_registration(obj)) or (try_to_insert_obj_to_db(obj, 'create')):
        print('Успешно!')


def remove_obj_by_admin(model_class: model_classes_for_admin_work) -> None:
    """Позволяет администратору удалить объект из системы"""

    obj = get_obj_from_user_for_admin_work(model_class, 'Нет объектов для удаления!')
    if obj is None:
        return
    if model_class is Period and obj.pk == Period.manager.get(is_current=True).pk:
        print_error('Невозможно удалить текущий период успеваемости!')
        return
    if model_class in dependent_models:
        warn_user_about_dependent_models(model_class)
    finish_deleting_object(obj)


def change_obj_by_admin(model_class: model_classes_for_admin_work) -> None:
    """Позволяет администратору изменить объект"""

    obj = get_obj_from_user_for_admin_work(model_class, 'Нет объектов для изменения!')
    if obj is None:
        return
    attrs_to_change = get_attrs_to_change(obj)
    attr_en = attrs_to_change[get_obj_from_user(list(attrs_to_change.keys()), 'поле для измнения:')]
    attr_ru = model_class.attributes_ru[model_class.attributes.index(attr_en) - 1]
    if model_class is Period:
        print('Дата ставится в формате: (день/месяц/год)')
    try:
        new_raw_value = request_value_to_create_obj_by_admin(model_class, attr_en, attr_ru)
    except InvalidData:
        print_error('Неккоректные данные!')
        return
    new_processed_value = process_value_from_admin_to_change_obj(new_raw_value, attr_en, model_class)
    try:
        setattr(obj, attr_en, new_processed_value)
    except ValidationError as e:
        print_error(str(e))
        return
    print_obj_with_this_data_msg(obj)
    save_obj_msg()
    if try_to_insert_obj_to_db(obj, 'save'):
        print('Объект сохранен')
    else:
        print('Объект не сохранен')
