from stream_django.feed_manager import feed_manager
from stream.exceptions import DoesNotExistException
from stream_django.client import stream_client
from django.core.mail import send_mail
import boto3
from django.conf import settings
from django.db.models import F
import re
from django.utils.html import strip_tags
from django.template.loader import get_template

from catalog.general.models import get_translation_by_code
from django.core.exceptions import ObjectDoesNotExist
from botocore.exceptions import ClientError
import threading


def textify(html):
    # Remove html tags and continuous whitespaces
    text_only = re.sub('[ \t]+', ' ', strip_tags(html))
    # Strip single spaces in the beginning of each line
    return text_only.replace('\n ', '\n').strip()


def get_post_feed_name_and_id(instance):
    feed_id = 0
    feed_name = ''
    if instance.community:
        feed_name = 'community' + str(instance.type.feed_id)
        feed_id = instance.community.id
    if instance.community is None and instance.company:
        feed_name = 'company' + str(instance.type.feed_id)
        feed_id = instance.company.id
    if instance.community is None and instance.company is None:
        feed_name = 'user' + str(instance.type.feed_id)
        feed_id = instance.user.id
    return {'feed_name': feed_name, 'feed_id': feed_id}


def add_feed_activity(feed_name, feed_id, verb, actor, feed_object, target, foreign_id, create_date):
    feed = feed_manager.get_feed(feed_name, feed_id)

    activity_data = {'actor': actor, 'verb': verb, 'object': feed_object,
                     'target': target,
                     'foreign_id': foreign_id, 'time': create_date}
    feed.add_activity(activity_data)


def create_feed_activity(instance):
    model_name = instance.__class__.__name__

    if model_name == 'Post':
        update_feed = True
        if instance.shared_post:
            update_feed = get_update_user_feed_status(instance.shared_post)
        if update_feed:
            feed_obj = get_post_feed_name_and_id(instance)
            feed_id = feed_obj['feed_id']
            feed_name = feed_obj['feed_name']
            actor = 'auth.User:' + str(instance.user.id)
            verb = 'post'
            feed_object = 'post.Post:' + str(instance.id)
            target = 'post.Post:' + str(instance.id)
            foreign_id = 'post.Post:' + str(instance.id)
            time = instance.create_date
            add_feed_activity(feed_name, feed_id, verb, actor, feed_object, target, foreign_id, time)

    if model_name == 'PostFilterFeed':
        feed_name = 'filter' + str(instance.post.type.feed_id)
        feed_id = instance.filter_id
        actor = 'post.PostSEOData:' + str(feed_id)
        verb = 'filter'
        feed_object = 'post.Post:' + str(instance.post.id)
        target = 'post.Post:' + str(instance.post.id)
        foreign_id = 'post.PostFilterFeed:' + str(instance.id)
        time = instance.create_date
        add_feed_activity(feed_name, feed_id, verb, actor, feed_object, target, foreign_id, time)

    if model_name == 'PostLike':
        feed_name = 'user' + str(instance.post.type.feed_id)
        feed_id = instance.user.id
        actor = 'auth.User:' + str(instance.user.id)
        verb = 'like'
        feed_object = 'post.PostLike:' + str(instance.id)
        target = 'post.Post:' + str(instance.post.id)
        foreign_id = 'post.PostLike:' + str(instance.id)
        time = instance.create_date
        if get_update_user_feed_status(instance.post):
            add_feed_activity(feed_name, feed_id, verb, actor, feed_object, target, foreign_id, time)
        n_object = feed_object
        n_foreign_id = 'n_post.PostLike:' + str(instance.id)
        create_notification(instance.post.user, verb, actor, n_object, target, n_foreign_id, time)

    if model_name == 'PostComment':
        feed_name = 'user' + str(instance.post.type.feed_id)
        feed_id = instance.user.id
        actor = 'auth.User:' + str(instance.user.id)
        verb = 'comment'
        feed_object = 'post.PostComment:' + str(instance.id)
        target = 'post.Post:' + str(instance.post.id)
        foreign_id = 'post.PostComment:' + str(instance.id)
        time = instance.create_date
        if get_update_user_feed_status(instance.post):
            add_feed_activity(feed_name, feed_id, verb, actor, feed_object, target, foreign_id, time)
        n_foreign_id = 'n_post.PostComment:' + str(instance.id)
        n_object = feed_object
        if instance.user != instance.post.user:
            create_notification(instance.post.user, verb, actor, n_object, target, n_foreign_id, time,
                                message=instance.text)

        if instance.parent:
            if instance.parent.user != instance.user and instance.parent.user != instance.post.user:
                create_notification(instance.parent.user, verb, actor, feed_object, target, foreign_id, time,
                                    message=instance.text)
        if instance.reply_to and instance.reply_to != instance.post.user and instance.reply_to != instance.user:
            if not instance.parent:
                create_notification(instance.reply_to, verb, actor, feed_object, target, foreign_id, time,
                                    message=instance.text)
            else:
                if instance.parent.user != instance.reply_to:
                    create_notification(instance.reply_to, verb, actor, feed_object, target, foreign_id, time,
                                        message=instance.text)

    if model_name == 'PostCommentLike':

        feed_name = 'user' + str(instance.comment.post.type.feed_id)
        feed_id = instance.user.id
        actor = 'auth.User:' + str(instance.user.id)
        verb = 'comment_like'
        feed_object = 'post.PostComment:' + str(instance.comment.id)
        target = 'post.Post:' + str(instance.comment.post.id)
        foreign_id = 'post.PostCommentLike:' + str(instance.id)
        time = instance.create_date
        if get_update_user_feed_status(instance.comment.post):
            add_feed_activity(feed_name, feed_id, verb, actor, feed_object, target, foreign_id, time)
        n_foreign_id = 'n_post.PostCommentLike:' + str(instance.id)
        n_object = 'post.PostCommentLike:' + str(instance.comment.id)
        n_target = 'post.PostComment:' + str(instance.comment.id)
        n_verb = 'comment_like'

        if instance.user != instance.comment.user:
            create_notification(instance.comment.user, n_verb, actor, n_object, n_target, n_foreign_id, time,
                                message='')


def delete_activity_by_instance(instance):
    model_name = instance.__class__.__name__
    if model_name == 'Post':
        update_feed = True
        if instance.shared_post:
            update_feed = get_update_user_feed_status(instance.shared_post)

        if update_feed:
            feed_obj = get_post_feed_name_and_id(instance)
            feed_id = feed_obj['feed_id']
            feed_name = feed_obj['feed_name']
            foreign_id = 'post.Post:' + str(instance.id)
            delete_activity(feed_name, feed_id, foreign_id)

    if model_name == 'PostFilterFeed':
        feed_name = 'filter' + str(instance.post.type.feed_id)
        feed_id = instance.filter.id
        foreign_id = 'post.PostFilterFeed:' + str(instance.id)
        if get_update_user_feed_status(instance.post):
            delete_activity(feed_name, feed_id, foreign_id)

    if model_name == 'PostLike':
        feed_name = 'user' + str(instance.post.type.feed_id)
        feed_id = instance.user.id
        foreign_id = 'post.PostLike:' + str(instance.id)
        if get_update_user_feed_status(instance.post):
            delete_activity(feed_name, feed_id, foreign_id)
        n_foreign_id = 'n_post.PostLike:' + str(instance.id)
        delete_notification(instance.post.user_id, n_foreign_id)

    if model_name == 'PostComment':
        feed_name = 'user' + str(instance.post.type.feed_id)
        feed_id = instance.user.id
        foreign_id = 'post.PostComment:' + str(instance.id)
        if get_update_user_feed_status(instance.post):
            delete_activity(feed_name, feed_id, foreign_id)
        n_foreign_id = 'n_post.PostComment:' + str(instance.id)
        delete_notification(instance.post.user_id, n_foreign_id)

        if instance.reply_to:
            delete_notification(instance.reply_to, n_foreign_id)

        try:
            if instance.parent:
                delete_notification(instance.parent.user_id, n_foreign_id)
        except ObjectDoesNotExist:
            pass

    if model_name == 'PostCommentLike':
        feed_name = 'user' + str(instance.comment.post.type.feed_id)
        feed_id = instance.user.id
        foreign_id = 'post.PostCommentLike:' + str(instance.id)
        if get_update_user_feed_status(instance.comment.post):
            delete_activity(feed_name, feed_id, foreign_id)
        n_foreign_id = 'n_post.PostCommentLike:' + str(instance.id)
        delete_notification(instance.comment.user_id, n_foreign_id)


def follow_target_feed(target_name, user_id, target_id):
    """
    following feeds of a new target
    """
    follows = []

    for i in range(0, 8):
        target_str = target_name
        timeline_str = 'timeline_aggregated'
        feed_str = ':'

        if i > 0:
            feed_str = str(i) + ':'
            timeline_obj = {'source': timeline_str + feed_str + str(user_id),
                            'target': target_str + feed_str + str(target_id)}
            follows.append(timeline_obj)

        if target_name != 'tag' or i > 0:
            user_obj = {'source': timeline_str + ':' + str(user_id),
                        'target': target_str + feed_str + str(target_id)}
            follows.append(user_obj)

    stream_client.follow_many(follows, activity_copy_limit=10)


def unfollow_target_feed(target_name, user_id, target_id):
    """
        Unfollow feeds of a target
    """
    feed = feed_manager.get_feed('timeline_aggregated', user_id)

    for i in range(0, 8):
        target_str = target_name
        timeline_str = 'timeline_aggregated'
        if i > 0:
            target_str += str(i)
            timeline_str += str(i)
            feed_timeline = feed_manager.get_feed(timeline_str, user_id)
            feed_timeline.unfollow(target_str, target_id)

        if target_name != 'tag' or i > 0:
            feed.unfollow(target_str, target_id)


def prepare_message_content(template, lang, instance):
    model_name = instance.__class__.__name__
    logo_url = settings.LOGO_URL
    main_url = settings.FRONTEND_URL
    htmly = get_template(lang + '/' + template + '.html')
    plaintext = get_template(lang + '/' + template + '.txt')

    subject = ''
    html_content = ''
    text_content = ''

    if template == 'user_message':

        if instance.company:
            sender_dict = instance.company.get_email_dict(lang)
        else:
            sender_dict = instance.user.user_profile.get_email_dict(lang)

        subject_text = get_translation_by_code('message-from', lang)
        subject = subject_text + ' ' + sender_dict['name']

        read_more_url = settings.FRONTEND_URL + 'messaging/' + str(instance.chat_id)
        message = ''
        if instance.message:
            message = instance.message
        content = (
            {'username': sender_dict['name'], 'message': message, 'user_image': sender_dict['image'],
             'user_headline': sender_dict['headline'],
             'user_url': sender_dict['url'], 'read_more_url': read_more_url, 'logo_url': logo_url,
             'main_url': main_url})
        html_content = htmly.render(content)
        content = (
            {'username': sender_dict['name'], 'message': textify(message)})

        text_content = plaintext.render(content)

    if template == 'customer_request':

        if instance.customer_company:
            sender_dict = instance.customer_company.get_email_dict(lang)
        else:
            sender_dict = instance.customer_user.user_profile.get_email_dict(lang)

        subject_text = get_translation_by_code('new-customer-request-from', lang)
        subject = subject_text + ' ' + sender_dict['name']

        read_more_url = settings.FRONTEND_URL + 'requests/supplier'
        message = ''
        if instance.customer_comment:
            message = instance.customer_comment
        content = (
            {'username': sender_dict['name'], 'message': message, 'user_image': sender_dict['image'],
             'user_headline': sender_dict['headline'],
             'user_url': sender_dict['url'], 'read_more_url': read_more_url, 'request_id': instance.id,
             'logo_url': logo_url,
             'main_url': main_url})
        html_content = htmly.render(content)
        content = (
            {'username': sender_dict['name'], 'request_id': instance.id, 'message': textify(message)})

        text_content = plaintext.render(content)

    if template == 'customer_request_status':

        if instance.supplier_company:
            sender_dict = instance.supplier_company.get_email_dict(lang)
        else:
            sender_dict = instance.supplier_user.user_profile.get_email_dict(lang)
        status = instance.status.get_status_name_in_lang(lang)
        subject_text1 = get_translation_by_code('supply-request', lang)
        subject_text2 = get_translation_by_code('status-changed', lang)
        subject = subject_text1 + ' №' + str(instance.id) + '. ' + subject_text2 + ' - ' + status

        read_more_url = settings.FRONTEND_URL + 'requests/customer'

        content = (
            {'username': sender_dict['name'], 'status': status, 'user_image': sender_dict['image'],
             'user_headline': sender_dict['headline'],
             'user_url': sender_dict['url'], 'read_more_url': read_more_url, 'request_id': instance.id,
             'logo_url': logo_url,
             'main_url': main_url})
        html_content = htmly.render(content)
        content = (
            {'username': sender_dict['name'], 'request_id': instance.id, 'status': status})

        text_content = plaintext.render(content)

    if template == 'job_post_response':
        sender_dict = instance.user.user_profile.get_email_dict(lang)

        subject_text1 = get_translation_by_code('new-applicant', lang)
        subject_text2 = get_translation_by_code('vacancy', lang)
        subject = sender_dict['name'] + '. ' + subject_text1 + ' ' + instance.post.post_title + ' ' + subject_text2

        read_more_url = settings.FRONTEND_URL + 'responds/owner/job/'

        job_title = instance.post.post_title
        job_url = settings.FRONTEND_URL + 'post/' + str(instance.post_id)
        cv_name = ''
        cv_url = '#'
        message = ''
        if instance.cover_letter:
            message = instance.cover_letter

        if instance.resume:
            cv_name = instance.resume.name
            cv_url = instance.resume.file.url

        content = (
            {'username': sender_dict['name'], 'user_image': sender_dict['image'],
             'user_headline': sender_dict['headline'],
             'user_url': sender_dict['url'], 'read_more_url': read_more_url, 'request_id': instance.id,
             'logo_url': logo_url,
             'main_url': main_url, 'job_title': job_title, 'job_url': job_url, 'cv_name': cv_name, 'cv_url': cv_url,
             'message': message})
        html_content = htmly.render(content)

        content = (
            {'username': sender_dict['name'], 'job_title': job_title, 'message': message})
        text_content = plaintext.render(content)

    if template == 'post_response':
        sender_dict = instance.user.user_profile.get_email_dict(lang)
        subject_text1 = ''
        responds_path = ''
        read_more_text = ''
        response_type_text = ''

        if instance.post.type.code == 'offering':
            subject_text1 = get_translation_by_code('offering-response', lang)
            read_more_text = get_translation_by_code('responses-to-your-offerings', lang)
            response_type_text = get_translation_by_code('new-offering-response', lang)
            responds_path = 'owner/offering/'

        if instance.post.type.code == 'request':
            subject_text1 = get_translation_by_code('request-response', lang)
            read_more_text = get_translation_by_code('responses-to-your-requests', lang)
            response_type_text = get_translation_by_code('new-request-response', lang)
            responds_path = 'owner/request/'

        currency = ''
        price = ''
        if instance.currency:
            currency = instance.currency.code
        if instance.proposed_price:
            price = str(instance.proposed_price)

        subject = sender_dict['name'] + ' ' + subject_text1

        read_more_url = settings.FRONTEND_URL + responds_path

        response_title = instance.post.post_title
        response_url = settings.FRONTEND_URL + 'post/' + str(instance.post_id)

        message = ''
        if instance.cover_letter:
            message = instance.cover_letter
        content = (
            {'username': sender_dict['name'], 'user_image': sender_dict['image'],
             'user_headline': sender_dict['headline'],
             'user_url': sender_dict['url'], 'read_more_url': read_more_url, 'request_id': instance.id,
             'response_title': response_title, 'response_url': response_url,
             'read_more_text': read_more_text, 'response_type_text': response_type_text,
             'message': message, 'currency': currency, 'price': price,
             'logo_url': logo_url,
             'main_url': main_url})
        html_content = htmly.render(content)

        content = (
            {'username': sender_dict['name'], 'response_type_text': response_type_text,
             'response_title': response_title, 'message': message, 'currency': currency, 'price': price})
        text_content = plaintext.render(content)

    if (template == 'administrator_created' or template == 'administrator_deleted') and (
            model_name == 'CompanyUser' or model_name == 'CommunityMember'):
        target_dict = dict()
        if model_name == 'CompanyUser':
            target_dict = instance.company.get_email_dict(lang)
        if model_name == 'CommunityMember':
            target_dict = instance.community.get_email_dict(lang)

        admin_dict = instance.user.user_profile.get_email_dict(lang)

        if template == 'administrator_created':
            subject_text = get_translation_by_code('new-administrator', lang)
        else:
            subject_text = get_translation_by_code('administrator-deleted', lang)

        subject = target_dict['name'] + '. ' + subject_text

        content = (
            {'username': admin_dict['name'], 'user_image': admin_dict['image'],
             'user_headline': admin_dict['headline'],
             'user_url': admin_dict['url'],
             'target_name': target_dict['name'], 'target_image': target_dict['image'],
             'target_url': target_dict['url'],
             'logo_url': logo_url,
             'main_url': main_url})
        html_content = htmly.render(content)
        content = (
            {'username': admin_dict['name'], 'target_name': target_dict['name']})

        text_content = plaintext.render(content)

    if template == 'community_invitation':

        target_dict = instance.community.get_email_dict(lang)

        if instance.company:
            member_dict = instance.company.get_email_dict(lang)
        else:
            member_dict = instance.user.user_profile.get_email_dict(lang)

        subject_text = get_translation_by_code('membership-request', lang)

        subject = target_dict['name'] + '. ' + subject_text

        content = (
            {'username': member_dict['name'], 'user_image': member_dict['image'],
             'user_headline': member_dict['headline'],
             'user_url': member_dict['url'],
             'target_name': target_dict['name'], 'target_image': target_dict['image'],
             'target_url': target_dict['url'],
             'logo_url': logo_url,
             'main_url': main_url})
        html_content = htmly.render(content)
        content = (
            {'username': member_dict['name'], 'target_name': target_dict['name']})

        text_content = plaintext.render(content)

    if template == 'community_member':

        target_dict = instance.community.get_email_dict(lang)

        if model_name == 'CommunityCompany':
            member_dict = instance.company.get_email_dict(lang)
        else:
            member_dict = instance.user.user_profile.get_email_dict(lang)

        subject_text = get_translation_by_code('community-member', lang)

        subject = target_dict['name'] + '. ' + subject_text

        content = (
            {'username': member_dict['name'], 'user_image': member_dict['image'],
             'user_headline': member_dict['headline'],
             'user_url': member_dict['url'],
             'target_name': target_dict['name'], 'target_image': target_dict['image'],
             'target_url': target_dict['url'], 'message': target_dict['rules'],
             'logo_url': logo_url,
             'main_url': main_url})
        html_content = htmly.render(content)
        content = (
            {'username': member_dict['name'], 'target_name': target_dict['name']})

        text_content = plaintext.render(content)

    res = dict()
    res['subject'] = subject
    res['html'] = html_content
    res['text'] = text_content
    return res


def delete_activity(feed_name, feed_id, foreign_id):
    feed = feed_manager.get_feed(feed_name, feed_id)
    try:
        feed.remove_activity(foreign_id=foreign_id)
    except DoesNotExistException:
        pass


def create_notification_by_instance_threading(instance, event_verb=None):
    model_name = instance.__class__.__name__

    if model_name == 'Message':
        if instance.company:
            objects = instance.chat.chat_users.exclude(company=instance.company)
        else:
            objects = instance.chat.chat_users.exclude(user=instance.user)

        objects.update(unread_messages=F('unread_messages') + 1)

        for obj in objects:
            if obj.company:
                obj.company.eventsqty.update_events_qty('new_messages', 1)
            else:
                obj.user.user_profile.eventsqty.update_events_qty('new_messages', 1)

        if objects:
            message_verb = ' message'
            if instance.type == 5:
                message_verb = ' request message'

            if instance.company:
                actor_type = 'company'
                actor = 'company.Company:' + str(instance.company_id)
            else:
                actor_type = 'user'
                actor = 'auth.User:' + str(instance.user_id)

            verb = actor_type + message_verb
            n_object = 'messaging.Message:' + str(instance.id)
            foreign_id = 'messaging.Message:' + str(instance.id)
            time = instance.create_date
            message = instance.message
            target = 'messaging.Chat:' + str(instance.chat_id)

            for participant in objects:
                if participant.user:

                    create_notification(participant.user, verb, actor, n_object, target, foreign_id, time,
                                        message=message)

                    if participant.user.user_profile.email and participant.user.user_profile.message_email:
                        lang = participant.user.user_profile.interface_lang.code
                        message_content = prepare_message_content('user_message', lang, instance)

                        send_message_notification(participant.user.user_profile.email, message_content['subject'],
                                                  message_content['html'], message_content['text'])
                else:
                    company_users = participant.company.users
                    for company_user in company_users.all():
                        create_notification(company_user.user, verb, actor, n_object, target, foreign_id, time,
                                            message=message)
                        if company_user.user.user_profile.email and company_user.user.user_profile.message_email:
                            lang = company_user.user.user_profile.interface_lang.code
                            message_content = prepare_message_content('user_message', lang, instance)

                            send_message_notification(company_user.user.user_profile.email, message_content['subject'],
                                                      message_content['html'], message_content['text'])

    if model_name == 'SupplyRequest' and not event_verb:
        message_verb = '_customer_request'

        if instance.customer_company:
            actor_type = 'company'
            actor = 'company.Company:' + str(instance.customer_company_id)
        else:
            actor_type = 'user'
            actor = 'auth.User:' + str(instance.customer_user_id)

        verb = actor_type + message_verb
        n_object = 'supply_request.SupplyRequest:' + str(instance.id)
        foreign_id = 'supply_request.SupplyRequest_new:' + str(instance.id)
        time = instance.create_date

        if instance.supplier_company:
            verb = verb + '_to_company'
            target = 'company.Company:' + str(instance.supplier_company_id)
            users = instance.supplier_company.users.filter(admin=True)
            for user in users.all():
                create_notification(user.user, verb, actor, n_object, target, foreign_id, time)
                if user.user.user_profile.email and user.user.user_profile.message_email:
                    lang = user.user.user_profile.interface_lang.code
                    message_content = prepare_message_content('customer_request', lang, instance)

                    send_message_notification(user.user.user_profile.email, message_content['subject'],
                                              message_content['html'], message_content['text'])

        else:
            verb = verb + '_to_user'
            target = 'user_profile.UserProfile:' + str(instance.supplier_user.user_profile.id)
            create_notification(instance.supplier_user, verb, actor, n_object, target, foreign_id, time)
            if instance.supplier_user.user_profile.email and instance.supplier_user.user_profile.message_email:
                lang = instance.supplier_user.user_profile.interface_lang.code
                message_content = prepare_message_content('customer_request', lang, instance)
                send_message_notification(instance.supplier_user.user_profile.email, message_content['subject'],
                                          message_content['html'], message_content['text'])

    if model_name == 'SupplyRequest' and event_verb == 'status_changed':
        message_verb = '_customer_request_status_' + instance.status.code

        if instance.status.code != 'c_canceled' and instance.status.code != 'confirmed':
            if instance.supplier_company:
                actor_type = 'company'
                actor = 'company.Company:' + str(instance.supplier_company_id)
            else:
                actor_type = 'user'
                actor = 'auth.User:' + str(instance.supplier_user_id)
        else:
            if instance.customer_company:
                actor_type = 'company'
                actor = 'company.Company:' + str(instance.customer_company_id)
            else:
                actor_type = 'user'
                actor = 'auth.User:' + str(instance.customer_user_id)

        verb = actor_type + message_verb
        n_object = 'supply_request.SupplyRequest:' + str(instance.id)
        foreign_id = 'supply_request.SupplyRequest:' + str(instance.id) + 's' + str(instance.status_id)
        time = instance.create_date
        message = instance.status.code
        if instance.status.code != 'c_canceled' and instance.status.code != 'confirmed':
            if instance.customer_company:
                target = 'company.Company:' + str(instance.customer_company_id)
                instance.customer_company.eventsqty.update_events_qty('new_messages', 1)

                users = instance.customer_company.users.filter(admin=True)
                for user in users.all():
                    create_notification(user.user, verb, actor, n_object, target, foreign_id, time, message)
                    if user.user.user_profile.email and user.user.user_profile.message_email:
                        lang = user.user.user_profile.interface_lang.code
                        message_content = prepare_message_content('customer_request_status', lang, instance)

                        send_message_notification(user.user.user_profile.email, message_content['subject'],
                                                  message_content['html'], message_content['text'])

            else:
                target = 'user_profile.UserProfile:' + str(instance.customer_user.user_profile.id)
                create_notification(instance.customer_user, verb, actor, n_object, target, foreign_id, time, message)
                instance.customer_user.user_profile.eventsqty.update_events_qty('new_messages', 1)
                if instance.customer_user.user_profile.email and instance.customer_user.user_profile.message_email:
                    lang = instance.customer_user.user_profile.interface_lang.code
                    message_content = prepare_message_content('customer_request_status', lang, instance)
                    send_message_notification(instance.customer_user.user_profile.email, message_content['subject'],
                                              message_content['html'], message_content['text'])
        else:
            if instance.supplier_company:
                verb = verb + '_to_company'
                target = 'company.Company:' + str(instance.supplier_company_id)
                instance.supplier_company.eventsqty.update_events_qty('new_messages', 1)

                users = instance.supplier_company.users.filter(admin=True)
                for user in users.all():
                    create_notification(user.user, verb, actor, n_object, target, foreign_id, time, message)
                    if user.user.user_profile.email and user.user.user_profile.message_email:
                        lang = user.user.user_profile.interface_lang.code
                        message_content = prepare_message_content('customer_request_status', lang, instance)

                        send_message_notification(user.user.user_profile.email, message_content['subject'],
                                                  message_content['html'], message_content['text'])

            else:
                target = 'user_profile.UserProfile:' + str(instance.supplier_user.user_profile.id)
                create_notification(instance.supplier_user, verb, actor, n_object, target, foreign_id, time, message)
                instance.supplier_user.user_profile.eventsqty.update_events_qty('new_messages', 1)
                if instance.supplier_user.user_profile.email and instance.supplier_user.user_profile.message_email:
                    lang = instance.supplier_user.user_profile.interface_lang.code
                    message_content = prepare_message_content('customer_request_status', lang, instance)
                    send_message_notification(instance.supplier_user.user_profile.email, message_content['subject'],
                                              message_content['html'], message_content['text'])

    if model_name == 'Applicant':
        verb = 'job_post_response'
        actor = 'auth.User:' + str(instance.user_id)
        n_object = 'post.Applicant:' + str(instance.id)
        foreign_id = 'post.Applicant:' + str(instance.id)
        time = instance.create_date
        target = 'post.Post:' + str(instance.post_id)
        if instance.post.company:

            users = instance.post.company.users.filter(admin=True)
            for user in users.all():
                create_notification(user.user, verb, actor, n_object, target, foreign_id, time)
                if user.user.user_profile.email and user.user.user_profile.message_email:
                    lang = user.user.user_profile.interface_lang.code
                    message_content = prepare_message_content(verb, lang, instance)
                    send_message_notification(user.user.user_profile.email, message_content['subject'],
                                              message_content['html'], message_content['text'])
        else:
            create_notification(instance.post.user, verb, actor, n_object, target, foreign_id, time)

            if instance.post.user.user_profile.email and instance.post.user.user_profile.message_email:
                lang = instance.post.user.user_profile.interface_lang.code
                message_content = prepare_message_content(verb, lang, instance)
                send_message_notification(instance.post.user.user_profile.email, message_content['subject'],
                                          message_content['html'], message_content['text'])

    if model_name == 'PostRespond':
        message_verb = ' ' + instance.post.type.code + '_post_response'

        if instance.company:
            actor_type = 'company'
            actor = 'company.Company:' + str(instance.company_id)
        else:
            actor_type = 'user'
            actor = 'auth.User:' + str(instance.user_id)

        verb = actor_type + message_verb

        n_object = 'post.PostRespond:' + str(instance.id)
        foreign_id = 'post.PostRespond:' + str(instance.id)
        time = instance.create_date
        target = 'post.Post:' + str(instance.post_id)
        if instance.post.company:

            users = instance.post.company.users.filter(admin=True)
            for user in users.all():
                create_notification(user.user, verb, actor, n_object, target, foreign_id, time)
                if user.user.user_profile.email and user.user.user_profile.message_email:
                    lang = user.user.user_profile.interface_lang.code
                    message_content = prepare_message_content('post_response', lang, instance)
                    send_message_notification(user.user.user_profile.email, message_content['subject'],
                                              message_content['html'], message_content['text'])
        else:
            create_notification(instance.post.user, verb, actor, n_object, target, foreign_id, time)

            if instance.post.user.user_profile.email and instance.post.user.user_profile.message_email:
                lang = instance.post.user.user_profile.interface_lang.code
                message_content = prepare_message_content('post_response', lang, instance)
                send_message_notification(instance.post.user.user_profile.email, message_content['subject'],
                                          message_content['html'], message_content['text'])

    if model_name == 'CompanyUser':
        verb = 'company_' + event_verb
        actor = 'auth.User:' + str(instance.user_id)
        n_object = 'company.Company:' + str(instance.company_id)
        foreign_id = verb + ':' + str(instance.id)
        time = instance.create_date
        target = 'company.Company:' + str(instance.company_id)

        for user in instance.company.users.all():
            create_notification(user.user, verb, actor, n_object, target, foreign_id, time)
            if user.user.user_profile.email and user.user.user_profile.notifications_email:
                lang = user.user.user_profile.interface_lang.code
                message_content = prepare_message_content(event_verb, lang, instance)
                send_message_notification(user.user.user_profile.email, message_content['subject'],
                                          message_content['html'], message_content['text'])
        if event_verb == 'administrator_deleted':
            create_notification(instance.user, verb, actor, n_object, target, foreign_id, time)
            if instance.user.user_profile.email and instance.user.user_profile.notifications_email:
                lang = instance.user.user_profile.interface_lang.code
                message_content = prepare_message_content(event_verb, lang, instance)

                send_message_notification(instance.user.user_profile.email, message_content['subject'],
                                          message_content['html'], message_content['text'])

    if model_name == 'CommunityMember' and (
            event_verb == 'administrator_created' or event_verb == 'administrator_deleted'):
        verb = 'community_' + event_verb

        actor = 'auth.User:' + str(instance.user_id)
        n_object = 'community.Community:' + str(instance.community_id)
        foreign_id = verb + ':' + str(instance.id)
        time = instance.create_date
        target = 'community.Community:' + str(instance.community_id)

        for user in instance.community.members.filter(admin=True):
            create_notification(user.user, verb, actor, n_object, target, foreign_id, time)
            if user.user.user_profile.email and user.user.user_profile.notifications_email:
                lang = user.user.user_profile.interface_lang.code
                message_content = prepare_message_content(event_verb, lang, instance)

                send_message_notification(user.user.user_profile.email, message_content['subject'],
                                          message_content['html'], message_content['text'])

        if event_verb == 'administrator_created':
            create_notification(instance.user, verb, actor, n_object, target, foreign_id, time)
            if instance.user.user_profile.email and instance.user.user_profile.notifications_email:
                lang = instance.user.user_profile.interface_lang.code
                message_content = prepare_message_content(event_verb, lang, instance)

                send_message_notification(instance.user.user_profile.email, message_content['subject'],
                                          message_content['html'], message_content['text'])

    if model_name == 'CommunityInvitation':

        message_verb = ' community_invitation'

        if instance.company:
            actor_type = 'company'
            actor = 'company.Company:' + str(instance.company_id)
        else:
            actor_type = 'user'
            actor = 'auth.User:' + str(instance.user_id)
        verb = actor_type + message_verb

        n_object = 'community.CommunityInvitation:' + str(instance.id)
        foreign_id = 'community.CommunityInvitation:' + str(instance.id)
        time = instance.create_date
        target = 'community.Community:' + str(instance.community_id)

        for user in instance.community.members.filter(admin=True):
            create_notification(user.user, verb, actor, n_object, target, foreign_id, time)
            if user.user.user_profile.email and user.user.user_profile.notifications_email:
                lang = user.user.user_profile.interface_lang.code
                message_content = prepare_message_content('community_invitation', lang, instance)

                send_message_notification(user.user.user_profile.email, message_content['subject'],
                                          message_content['html'], message_content['text'])

    if model_name == 'CommunityMember' and event_verb == 'user_community_member':
        verb = event_verb
        actor = 'auth.User:' + str(instance.user_id)
        n_object = 'community.CommunityMember:' + str(instance.id)
        foreign_id = 'community.CommunityMember:' + str(instance.id)
        time = instance.create_date
        target = 'community.Community:' + str(instance.community_id)
        create_notification(instance.user, verb, actor, n_object, target, foreign_id, time)
        if instance.user.user_profile.email and instance.user.user_profile.notifications_email:
            lang = instance.user.user_profile.interface_lang.code
            message_content = prepare_message_content('community_member', lang, instance)

            send_message_notification(instance.user.user_profile.email, message_content['subject'],
                                      message_content['html'], message_content['text'])

    if model_name == 'CommunityCompany':
        verb = 'company_community_member'
        actor = 'company.Company:' + str(instance.company_id)
        n_object = 'community.Community:' + str(instance.community_id)
        foreign_id = 'community.CommunityCompany:' + str(instance.id)
        time = instance.create_date
        target = 'community.Community:' + str(instance.community_id)
        for user in instance.company.users.all():
            create_notification(user.user, verb, actor, n_object, target, foreign_id, time)
            if user.user.user_profile.email and user.user.user_profile.notifications_email:
                lang = user.user.user_profile.interface_lang.code
                message_content = prepare_message_content('community_member', lang, instance)
                send_message_notification(user.user.user_profile.email, message_content['subject'],
                                          message_content['html'], message_content['text'])

    if model_name == 'CompanyFollower':
        verb = 'company_follower'
        actor = 'auth.User:' + str(instance.user_id)
        n_object = 'company.Company:' + str(instance.company_id)
        foreign_id = 'company.CompanyFollower_n:' + str(instance.id)
        time = instance.create_date
        target = 'company.Company:' + str(instance.company_id)
        for user in instance.company.users.all():
            create_notification(user.user, verb, actor, n_object, target, foreign_id, time)

    if model_name == 'UserProfileFollower':
        verb = 'profile_follower'
        actor = 'auth.User:' + str(instance.user_id)
        n_object = 'user_profile.UserProfile:' + str(instance.profile.id)
        foreign_id = 'user_profile.UserProfileFollower:' + str(instance.id)
        time = instance.create_date
        target = 'user_profile.UserProfile:' + str(instance.profile.id)
        create_notification(instance.profile.user, verb, actor, n_object, target, foreign_id, time)

    if model_name == 'SuggestedCategory':
        if not instance.reviewed:
            verb = 'category_suggested'
            actor = 'company.Company:' + str(settings.UAFINE_ID)
            n_object = str(instance.id)
            foreign_id = 'category.SuggestedCategory:' + str(instance.id)
            time = instance.create_date
            target = 'category.SuggestedCategory:' + str(instance.id)
            create_notification(instance.user, verb, actor, n_object, target, foreign_id, time)
            category_message = str(instance.id) + ' - ' + instance.name
            send_message_notification(settings.SUPPORT_EMAIL, 'A suggested category',
                                      category_message, category_message)

        if instance.reviewed:
            verb = 'new_category'
            actor = 'company.Company:' + str(settings.UAFINE_ID)
            n_object = 'category.SuggestedCategory:' + str(instance.id)
            foreign_id = 'category.Category:' + str(instance.category.id)
            time = instance.update_date
            target = 'category.Category:' + str(instance.category.id)
            create_notification(instance.user, verb, actor, n_object, target, foreign_id, time)


def create_notification_by_instance(instance, event_verb=None):
    t1 = threading.Thread(target=create_notification_by_instance_threading, args=(instance, event_verb,))
    t1.start()


def create_notification(user_instance, verb, actor, obj, target, foreign_id, create_date, message=''):
    try:
        user_instance.user_profile.eventsqty.notifications = user_instance.user_profile.eventsqty.notifications + 1
        user_instance.user_profile.eventsqty.save()
    except ObjectDoesNotExist:
        pass

    activity_data = {'actor': actor, 'verb': verb,
                     'object': obj,
                     'foreign_id': foreign_id,
                     'target': target,
                     'message': message,
                     'time': create_date}

    notification_feed = feed_manager.get_notification_feed(user_instance.id)

    notification_feed.add_activity(activity_data)


def delete_notification(user, foreign_id):
    notification_feed = feed_manager.get_notification_feed(str(user))
    try:
        notification_feed.remove_activity(foreign_id=foreign_id)
    except DoesNotExistException:
        pass


def get_update_user_feed_status(instance):
    update_user_feed = True

    if instance.community:
        update_user_feed = instance.community.open

    return update_user_feed


def send_message_notification(user_email, subject, message, text_message):
    client = boto3.client('ses',
                          aws_access_key_id=settings.AWS_SES_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SES_SECRET_ACCESS_KEY,
                          region_name='eu-west-1')

    response = client.get_identity_verification_attributes(
        Identities=[
            user_email,
        ]
    )
    attributes = response["VerificationAttributes"]

    if attributes:
        verification = attributes[user_email]["VerificationStatus"]

        if verification == "Success":
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.SUPPORT_EMAIL,
                    [user_email],
                    html_message=message
                )

            except ClientError as e:
                print(e.response['Error']['Message'])

    else:
        pass
