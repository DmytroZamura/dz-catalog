from django.core.management.base import BaseCommand
from catalog.category.models import Category, CategoryClassification, CategoryName
from django.template.defaultfilters import slugify
from django.db.models import Max
from django.db.models import Q


def create_default_names():
    categories = Category.objects.language('en').all()
    for category in categories:
        category.default_name = category.name
        category.save()


def set_first_level():
    Category.objects.language('en').filter(parent__isnull=True).update(first_level=True)


def update_classification_code(code, en_name, level):
    if level == 1:
        CategoryClassification.objects.filter(level1_en_name=en_name).update(level1_code=code)
    if level == 2:
        CategoryClassification.objects.filter(level2_en_name=en_name).update(level2_code=code)
    if level == 3:
        CategoryClassification.objects.filter(level3_en_name=en_name).update(level3_code=code)
    if level == 4:
        CategoryClassification.objects.filter(level4_en_name=en_name).update(level4_code=code)
    if level == 5:
        CategoryClassification.objects.filter(level5_en_name=en_name).update(level5_code=code)

def update_classification_position(code, position):

    CategoryClassification.objects.filter(level1_code = code).update(level1_position=position)
    CategoryClassification.objects.filter(level2_code=code).update(level2_position=position)
    CategoryClassification.objects.filter(level3_code=code).update(level3_position=position)
    CategoryClassification.objects.filter(level4_code=code).update(level4_position=position)
    CategoryClassification.objects.filter(level5_code=code).update(level5_position=position)
    CategoryClassification.objects.filter(level6_code=code).update(level6_position=position)


def update_classification_positions():
    categories = Category.objects.language('en').all()

    for category in categories:
        print(category.name)
        update_classification_position(category.pk, category.position)

def set_category_translation(instance, name_ru, name_uk):
    try:
        category = Category.objects.language('ru').get(id=instance.id)
    except Category.DoesNotExist:
        category = instance.translate('ru')
    category.name = name_ru
    category.save()

    try:
        category = Category.objects.language('uk').get(id=instance.id)
    except Category.DoesNotExist:
        category = instance.translate('uk')
    category.name = name_uk
    try:
        category.save()
    except:
        print('Ошибка - ' + name_ru)


def get_category_max_position(parent_id):
    items = Category.objects.language('en').filter(parent_id=parent_id)
    res = items.aggregate(Max('position'))
    current_max = res.get('position__max')
    if current_max:
        new_max = current_max + 5
    else:
        new_max = 5
    print(new_max)
    return new_max


def check_category(code, parent_id, position, name_en, name_ru, name_uk):
    if code or name_en:
        try:
            if code:
                category = Category.objects.language('en').get(pk=code)
            else:

                category = Category.objects.language('en').get(default_name=name_en)


            if not category.updated:
                print(name_ru)
                category.updated = True

                category.default_name = name_en
                category.name = name_en
                category.slug = slugify(category.default_name)
                category.parent_id = parent_id
                if position:
                    category.position = position
                else:
                    category.position = get_category_max_position(parent_id)
                set_category_translation(category, name_ru, name_uk)
                category.save()




        except Category.DoesNotExist:
            print(name_ru)

            if position:
                category_position = position
            else:
                category_position = get_category_max_position(parent_id)

            category = Category.objects.language('en').create(
                default_name=name_en,
                updated=True,
                approved=True,
                name=name_en,
                parent_id=parent_id,
                position=category_position
            )
            category.save()
            set_category_translation(category, name_ru, name_uk)

        return category
    else:
        return None


def update_categories_from_classification_by_names():
    Category.objects.language('en').all().update(updated=False)

    classification_rows = CategoryClassification.objects.all().order_by('id')
    for classification_row in classification_rows:
        level1_id = None
        level2_id = None
        level3_id = None
        level4_id = None
        level5_id = None

        if classification_row.level1_en_name:
            level1_id = check_category(classification_row.level1_code, None, classification_row.level1_position,
                                       classification_row.level1_en_name,
                                       classification_row.level1_ru_name,
                                       classification_row.level1_uk_name)
            if classification_row.level1_code != level1_id.pk:
                classification_row.level1_code = level1_id.pk
                classification_row.level1_position = level1_id.position
                classification_row.save()

        if level1_id and classification_row.level2_en_name:
            level2_id = check_category(classification_row.level2_code, level1_id.pk, classification_row.level2_position,
                                       classification_row.level2_en_name,
                                       classification_row.level2_ru_name,
                                       classification_row.level2_uk_name)
            if classification_row.level2_code != level2_id.pk:
                classification_row.level2_code = level2_id.pk
                classification_row.level2_position = level2_id.position
                classification_row.save()
        if level2_id and classification_row.level3_en_name:
            level3_id = check_category(classification_row.level3_code, level2_id.pk, classification_row.level3_position,
                                       classification_row.level3_en_name,
                                       classification_row.level3_ru_name,
                                       classification_row.level3_uk_name)
            if classification_row.level3_code != level3_id.pk:
                classification_row.level3_code = level3_id.pk
                classification_row.level3_position = level3_id.position
                classification_row.save()
        if level3_id and classification_row.level4_en_name:
            level4_id = check_category(classification_row.level4_code, level3_id.pk, classification_row.level4_position,
                                       classification_row.level4_en_name,
                                       classification_row.level4_ru_name,
                                       classification_row.level4_uk_name)
            if classification_row.level4_code != level4_id.pk:
                classification_row.level4_code = level4_id.pk
                classification_row.level4_position = level4_id.position
                classification_row.save()
        if level4_id and classification_row.level5_en_name:
            level5_id = check_category(classification_row.level5_code, level4_id.pk, classification_row.level5_position,
                                       classification_row.level5_en_name,
                                       classification_row.level5_ru_name,
                                       classification_row.level5_uk_name)
            if classification_row.level5_code != level5_id.pk:
                classification_row.level5_code = level5_id.pk
                classification_row.level5_position = level5_id.position
                classification_row.save()
        if level5_id and classification_row.level6_en_name:
            level6_id = check_category(classification_row.level6_code, level5_id.pk, classification_row.level6_position,
                                       classification_row.level6_en_name,
                                       classification_row.level6_ru_name,
                                       classification_row.level6_uk_name)
            if classification_row.level6_code != level6_id.pk:
                classification_row.level6_code = level6_id.pk
                classification_row.level6_position = level6_id.position
                classification_row.save()





def set_en_names_for_classification():
    categories = CategoryClassification.objects.all()
    for category in categories:
        if not category.level1_en_name and category.level1_code:
            print(category.level1_ru_name)
            category_name = CategoryName.objects.get(code=category.level1_code, lang='en')
            category.level1_en_name = category_name.name
            category.save()
        if not category.level2_en_name and category.level2_code:
            print(category.level2_ru_name)
            print(category.level2_code)
            category_name = CategoryName.objects.get(code=category.level2_code, lang='en')
            category.level2_en_name = category_name.name
            category.save()
        if not category.level3_en_name and category.level3_code:
            print(category.level3_ru_name)
            print(category.level3_code)
            category_name = CategoryName.objects.get(code=category.level3_code, lang='en')
            category.level3_en_name = category_name.name
            category.save()
        if not category.level4_en_name and category.level4_code:
            print(category.level4_ru_name)
            print(category.level4_code)
            category_name = CategoryName.objects.get(code=category.level4_code, lang='en')
            category.level4_en_name = category_name.name
            category.save()
        if not category.level5_en_name and category.level5_code:
            print(category.level5_code)
            print(category.level5_ru_name)
            try:
                category_name = CategoryName.objects.get(code=category.level5_code, lang='en')
                category.level5_en_name = category_name.name
                category.save()
            except CategoryName.DoesNotExist:
                print(category.level5_code)
                print(category.level5_ru_name)

        if not category.level6_en_name and category.level6_code:
            print(category.level6_ru_name)
            category_name = CategoryName.objects.get(code=category.level6_code, lang='en')
            category.level6_en_name = category_name.name
            category.save()


def get_parent_problem():
    problems = Category.objects.language('en').all()
    for problem in problems:
        if problem.parent:
            if problem.parent_id > problem.id:
                print(problem.name + ' - ' + str(problem.id))


def set_parent_null():
    Category.objects.language('en').all().update(parent=None)





# def init_categories_classification_codes():
#     classifications = CategoryClassification.objects.all()
#
#     for classification in classifications:
#         print(classification.level1_en_name)
#
#         try:
#            item = CategoryClassification.objects.filter(level1_en_name=classification.level1_en_name).first()
#         except: CategoryClassification.DoesNotExist:


class Command(BaseCommand):
    def handle(self, *args, **options):
        # create_default_names()
        # set_en_names_for_classification()
        # update_categories_from_classification()
        # get_parent_problem()
        # update_classification_code('a203020', 'Vehicles & Accessories', 2)
        # set_first_level()
        # set_parent_null()
        update_categories_from_classification_by_names()
        # update_classification_positions()
