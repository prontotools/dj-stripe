from __future__ import unicode_literals

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from mock import patch, PropertyMock
from djstripe.serializers import (
    SubscriptionSerializer,
    CreateSubscriptionSerializer,
)
from djstripe.models import (
    CurrentSubscription,
)


class SubscriptionSerializerTest(TestCase):

    def setup(self):
        pass

    def test_valid_serializer(self):
        now = timezone.now()
        serializer = SubscriptionSerializer(
            data={
                'plan': settings.DJSTRIPE_PLANS['test0']['plan'],
                'quantity': 2,
                'start': now,
                'status': CurrentSubscription.STATUS_ACTIVE,
                'amount': settings.DJSTRIPE_PLANS['test0']['price'],
            }
        )
        assert serializer.is_valid()
        assert serializer.validated_data == {
            'plan': 'test0',
            'quantity': 2,
            'start': now,
            'status': 'active',
            'amount': Decimal('1000'),
        }
        assert serializer.errors == {}

    def test_invalid_serializer(self):
        now = timezone.now()
        serializer = SubscriptionSerializer(
            data={
                'plan': settings.DJSTRIPE_PLANS['test0']['plan'],
                'start': now,
                'status': CurrentSubscription.STATUS_ACTIVE,
                'amount': settings.DJSTRIPE_PLANS['test0']['price'],
            }
        )
        assert not serializer.is_valid()
        assert serializer.validated_data == {}
        assert serializer.errors == {'quantity': ['This field is required.']}


class CreateSubscriptionSerializerTest(TestCase):

    def setup(self):
        pass

    @patch("stripe.Token.create", return_value=PropertyMock(id="token_test"))
    def test_valid_serializer(self, stripe_token_mock):
        token = stripe_token_mock(card={})
        serializer = CreateSubscriptionSerializer(
            data={
                'plan': settings.DJSTRIPE_PLANS['test0']['plan'],
                'stripe_token': token.id,
            }
        )
        assert serializer.is_valid()
        assert serializer.validated_data['plan'] == 'test0'
        self.assertIn('stripe_token', serializer.validated_data)
        assert serializer.errors == {}

    def test_invalid_serializer(self):
        serializer = CreateSubscriptionSerializer(
            data={
                'plan': settings.DJSTRIPE_PLANS['test0']['plan'],
            }
        )
        assert not serializer.is_valid()
        assert serializer.validated_data == {}
        assert serializer.errors == {
            'stripe_token': ['This field is required.'],
        }
