Nifty-Client
=======================================

Nifty Client is the official Python client for the nifty API.
It does some heavy lifting to provide a simple and portable client.
If you do find the client missing some features, please make a pull request
or cut an issue.



Installation
===============
Installing the client is simple with pip:

.. code-block:: sh

    pip install niftyclient


Quickstart
=============

After installing the client, get your api credentials from the nifty dashboard,
configure the client with the credentials and you are good to go.

.. code-block:: python

    from niftyclient import NiftyWalletClient

    class ExampleConfig:
        key_id = "f4664c39663272d70b7ebdc96ddac72e"
        secret = "4c198a69e108ce6f293734d4f0a511a0d1fd6bf70a26e9c2e5f147ff41615f9bf3b6349595aff7011ca28f806976715a"
        user_id = "15695297-f441-4b1c-a75b-831fbb1d1431"


    client = NiftyWalletClient(ExampleConfig())

    client.get_wallet()
    # Response is wallet response with no wallet
    # MutableDictionaryObject({'available_resultset_size': 0, 'tracking_uuid': UUID('89feedd2-2c51-11e7-bd4c-000c29e41bf4'), 'wallets': [] 'limit': 30, 'offset': 0, 'returned_resultset_size': 0})

    client.create_wallet()
    # wallet created.
    # MutableDictionaryObject({'available_resultset_size': 1, 'tracking_uuid': UUID('89feedd2-2c51-11e7-bd4c-000c29e41bf4'), 'wallets': [DictionaryObject({'user_name': u'mike', 'created_at': datetime.datetime(2017, 4, 24, 23, 33, 52, 747695, tzinfo=tzoffset(None, 10800)), 'balance': Decimal('0.00'), 'user_id': UUID('8dad2dea-7d7f-4e8b-a61c-53150f1b7452'), 'last_modified': datetime.datetime(2017, 4, 27, 21, 31, 15, 268358, tzinfo=tzoffset(None, 10800))})], 'limit': 30, 'offset': 0, 'returned_resultset_size': 1})
    client.create_wallet()
    # This operation is idempotent and will return the same result as above

    client.get_wallet()
    # MutableDictionaryObject({'available_resultset_size': 1, 'tracking_uuid': UUID('89feedd2-2c51-11e7-bd4c-000c29e41bf4'), 'wallets': [DictionaryObject({'user_name': u'mike', 'created_at': datetime.datetime(2017, 4, 24, 23, 33, 52, 747695, tzinfo=tzoffset(None, 10800)), 'balance': Decimal('0.00'), 'user_id': UUID('8dad2dea-7d7f-4e8b-a61c-53150f1b7452'), 'last_modified': datetime.datetime(2017, 4, 27, 21, 31, 15, 268358, tzinfo=tzoffset(None, 10800))})], 'limit': 30, 'offset': 0, 'returned_resultset_size': 1})

    # Consume token. This operation is not idempotent and is atomic.
    client.consume_token(
        transaction_id="2TR46IBB5C", phone_number="254722123456", till_number=703648)
    # MutableDictionaryObject({'transactions': [DictionaryObject({'till_number': u'703648', 'payment_id': UUID('d2c29c60-0b1a-11e7-8f7b-061cf2e0e94d'), 'user_id': UUID('8dad2dea-7d7f-4e8b-a61c-53150f1b7452'), 'trans_amount': Decimal('799.23'), 'msisdn': u'254722123456', 'trans_time': datetime.datetime(2016, 5, 29, 21, 30, 52, 739072, tzinfo=tzoffset(None, 10800)), 'names': u'First M Last', 'trans_id': u'2TR46IBB5C'})], 'tracking_uuid': UUID('3582b27e-2c52-11e7-bd4c-000c29e41bf4'), 'available_resultset_size': 1, 'limit': 0, 'offset': 0, 'returned_resultset_size': 1})

    # Operation should not succeed again
    client.consume_token(
        transaction_id="2TR46IBB5C", phone_number="254722123456", till_number=703648)
    # MutableDictionaryObject({'transactions': [], 'tracking_uuid': UUID('c63774da-2c52-11e7-bd4c-000c29e41bf4'), 'available_resultset_size': 0, 'limit': 0, 'offset': 0, 'returned_resultset_size': 0})

    # Any incorrect field will not return a redemption transaction.
    client.consume_token(
        transaction_id="2TR46IBB5C", phone_number="254716622446", till_number=703646)
    # MutableDictionaryObject({'transactions': [], 'tracking_uuid': UUID('c63774da-2c52-11e7-bd4c-000c29e41bf4'), 'available_resultset_size': 0, 'limit': 0, 'offset': 0, 'returned_resultset_size': 0})

    # Transactions list
    client.transactions()
    # MutableDictionaryObject({'transactions': [DictionaryObject({'till_number': u'703648', 'payment_id': UUID('d2c29c60-0b1a-11e7-8f7b-061cf2e0e94d'), 'user_id': UUID('8dad2dea-7d7f-4e8b-a61c-53150f1b7452'), 'trans_amount': Decimal('799.23'), 'msisdn': u'254722123456', 'trans_time': datetime.datetime(2016, 5, 29, 21, 30, 52, 739072, tzinfo=tzoffset(None, 10800)), 'names': u'First M Last', 'trans_id': u'2TR46IBB5C'}), DictionaryObject({'till_number': u'703648', 'payment_id': UUID('d2c29c60-0b1a-11e7-8f7b-061cf2e0e94d'), 'user_id': UUID('8dad2dea-7d7f-4e8b-a61c-53150f1b7452'), 'trans_amount': Decimal('581.37'), 'msisdn': u'254722123456', 'trans_time': datetime.datetime(2017, 1, 24, 21, 30, 52, 739243, tzinfo=tzoffset(None, 10800)), 'names': u'First M Last', 'trans_id': u'0OZC02Q1OZ'}), DictionaryObject({'till_number': u'703648', 'payment_id': UUID('d2c29c60-0b1a-11e7-8f7b-061cf2e0e94d'), 'user_id': UUID('8dad2dea-7d7f-4e8b-a61c-53150f1b7452'), 'trans_amount': Decimal('657.56'), 'msisdn': u'254722123456', 'trans_time': datetime.datetime(2017, 1, 31, 21, 30, 52, 739409, tzinfo=tzoffset(None, 10800)), 'names': u'First M Last', 'trans_id': u'3PEYGJ6IVK'}), DictionaryObject({'till_number': u'703648', 'payment_id': UUID('d2c29c60-0b1a-11e7-8f7b-061cf2e0e94d'), 'user_id': UUID('8dad2dea-7d7f-4e8b-a61c-53150f1b7452'), 'trans_amount': Decimal('837.30'), 'msisdn': u'254722123456', 'trans_time': datetime.datetime(2017, 2, 1, 21, 30, 52, 739964, tzinfo=tzoffset(None, 10800)), 'names': u'First M Last', 'trans_id': u'O65UCIF7I6'}), DictionaryObject({'till_number': u'703648', 'payment_id': UUID('d2c29c60-0b1a-11e7-8f7b-061cf2e0e94d'), 'user_id': UUID('8dad2dea-7d7f-4e8b-a61c-53150f1b7452'), 'trans_amount': Decimal('808.16'), 'msisdn': u'254722123456', 'trans_time': datetime.datetime(2017, 2, 15, 21, 30, 52, 740086, tzinfo=tzoffset(None, 10800)), 'names': u'First M Last', 'trans_id': u'ZJZCT31FQE'})], 'tracking_uuid': UUID('93b6845a-2c53-11e7-bf31-000c29e41bf4'), 'available_resultset_size': 5, 'limit': 30, 'offset': 0, 'returned_resultset_size': 5})
