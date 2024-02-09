import stream
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from stream_django.enrich import Enrich
from stream_django.feed_manager import feed_manager
from catalog.user_profile.serializers import UserWithProfileSmallSerializer


class UserTokenView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        client = stream.connect(settings.STREAM_API_KEY, settings.STREAM_API_SECRET)

        token = client.create_user_token(str(self.request.user.id))
        data = {'token': token}

        return Response(data)


user_actor_verbs = [
    'user message',
    'user request message',
    'user_customer_request_to_company',
    'user_customer_request_to_user',
    'user_customer_request_status',
    'job_post_response',
    'user_offering_post_response',
    'user_request_post_response',
    'company_administrator_created',
    'company_administrator_deleted',
    'community_administrator_created',
    'community_administrator_deleted',
    'user community_invitation',
    'user_community_member',
    'company_follower',
    'profile_follower',
    'like',
    'comment',
    'comment_like',
    'user_customer_request_status_new',
    'user_customer_request_status_processing',
    'user_customer_request_status_completed',
    'user_customer_request_status_canceled',
    'user_customer_request_status_confirm',
    'user_customer_request_status_confirmed',
    'user_customer_request_status_c_canceled',
    'user_customer_request_status_confirmed_to_company',
    'user_customer_request_status_c_canceled_to_company',
    'user offering_post_response',
    'user request_post_response'
]

post_respond_verbs = ['job_post_response',
                      'user offering_post_response', 'company offering_post_response', 'user request_post_response',
                      'company request_post_response']


def get_serialized_object_or_none(obj, class_name, context):
    def func_not_found():  # just in case we dont have the function
        print('No Function ' + class_name + ' Found!')

    if hasattr(obj, class_name):
        func = getattr(obj, class_name, func_not_found)
        func()  # <-- this should work!
        obj = func(obj, context=context).data

    else:
        obj = None  # Could also raise exception here
    return obj


def get_default_serialized_object_or_none(obj, class_name, context):
    def func_not_found():  # just in case we dont have the function
        print('No Function ' + class_name + ' Found!')

    if hasattr(obj, class_name):
        func = getattr(obj, class_name, func_not_found)
        func()  # <-- this should work!
        obj = func(obj, context=context, language='en').data

    else:
        obj = None  # Could also raise exception here
    return obj


def serialize_notification(request, activity, index, serializer):
    if activity['verb'] in user_actor_verbs:
        actor = UserWithProfileSmallSerializer(activity['actor'],
                                               context={'request': request}).data

    else:
        actor = get_serialized_object_or_none(activity['actor'], serializer,
                                              context={'request': request, })
        if actor:
            if 'name' in actor:
                if not actor['name']:
                    actor = get_default_serialized_object_or_none(activity['actor'],
                                                                  serializer,
                                                                  context={'request': request,
                                                                           })
        else:
            actor = None

    activity['actor'] = actor

    if index == 0:
        company = None

        target = get_serialized_object_or_none(activity['target'], serializer,
                                               context={'request': request,
                                                        'company': company})
        if target:
            if 'name' in target:
                if not target['name']:
                    target = get_default_serialized_object_or_none(activity['target'],
                                                                   serializer,
                                                                   context={'request': request,
                                                                            'company': company})
            if 'first_name' in target:
                if not target['first_name']:
                    target = get_default_serialized_object_or_none(activity['target'],
                                                                   serializer,
                                                                   context={'request': request,
                                                                            'company': company})

            activity['target'] = target




        else:
            activity['target'] = None
        obj = get_serialized_object_or_none(activity['object'], serializer,
                                            context={'request': request})

        if obj:
            activity['object'] = obj
        else:
            activity['object'] = None
    else:
        activity['object'] = None
        activity['target'] = None

    return activity


def serialize_notifications(request, activities):
    for item in activities:
        i = 0
        for activity in item['activities']:
            activity = serialize_notification(request, activity, i, settings.NOTIFICATION_SERIALIZER_CLASS)
            i = i + 1
            # print('activity')

    return activities


class NotificationsFeedView(APIView):
    permission_classes = (IsAuthenticated,)

    # @method_decorator(cache_page(60 * 5))
    # @method_decorator(vary_on_cookie)

    def get(self, request, page):
        enricher = Enrich(fields=['actor', 'target', 'object'])

        feed = feed_manager.get_feed('notification', request.user.id)
        if page == 0:
            activities = feed.get(limit=10, mark_seen='all')['results']
        else:
            item_from = int(page) * 10

            activities = feed.get(limit=10, offset=item_from, mark_seen='all')['results']

        enriched_activities = enricher.enrich_aggregated_activities(activities)

        serialized_activities = serialize_notifications(self.request, enriched_activities)
        # print(serialized_activities)

        return Response(serialized_activities)


class EnrichNotificationView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        enricher = Enrich(fields=['actor', 'target', 'object'])
        activities = [request.data]

        enriched_activities = enricher.enrich_activities(activities)
        serialized_activity = serialize_notification(self.request, enriched_activities[0], 0,
                                                     settings.ACTIVITY_SERIALIZER_CLASS)

        return Response(serialized_activity)
