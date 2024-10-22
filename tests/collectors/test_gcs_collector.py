# import asyncio
# import json
# from querent.collectors.collector_resolver import CollectorResolver
# from querent.collectors.gcs.gcs_collector import GCSCollectorFactory
# from querent.common.uri import Uri
# from querent.config.collector.collector_config import CollectorBackend, GcsCollectConfig
# import pytest
# import uuid
# from dotenv import load_dotenv

# load_dotenv()


# @pytest.fixture
# def gcs_config():
#     cred_file = "/tmp/.config/gcloud/application_default_credentials.json"
#     credentials_info = json.load(open(cred_file))
#     credential_json_str = json.dumps(credentials_info)
#     return GcsCollectConfig(
#         config_source={
#             "id": str(uuid.uuid4()),
#             "bucket": "querent-test",
#             "credentials": credential_json_str,
#             "chunk": "1024",
#             "config": {},
#             "name": "GCS-config",
#             "uri": "gcs://",
#         }
#     )


# def test_gcs_collector_factory():
#     factory = GCSCollectorFactory()
#     assert factory.backend() == CollectorBackend.Gcs


# # Modify this function to test the GCS collector

# # To do: uncomment the following code when you have the bucket name and the credentials.json file for testing.


# @pytest.mark.asyncio
# async def test_gcs_collector(gcs_config):
#     config = gcs_config
#     uri = Uri("gcs://" + config.bucket)
#     resolver = CollectorResolver()
#     collector = resolver.resolve(uri, config)
#     assert collector is not None

#     await collector.connect()

#     async def poll_and_print():
#         counter = 0
#         async for result in collector.poll():
#             assert not result.is_error()
#             chunk = result.unwrap()

#             if chunk is not None:
#                 counter += 1
#         assert counter >5

#     await poll_and_print()


# if __name__ == "__main__":
#     asyncio.run(test_gcs_collector())
