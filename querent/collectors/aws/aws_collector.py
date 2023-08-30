# import asyncio
# from typing import AsyncGenerator

# import aiofiles
# from querent.config.collector_config import CollectorBackend, S3CollectConfig
# from querent.collectors.collector_base import Collector
# from querent.collectors.collector_factory import CollectorFactory
# from querent.collectors.collector_result import CollectorResult
# from querent.common.uri import Uri
# import aiohttp
# import aiobotocore
# from aiobotocore.session import get_session


# class AWSCollector(Collector):
#     def __init__(self, config: S3CollectConfig):
#         self.bucket_name = config.bucket
#         self.region = config.region
#         self.access_key = config.access_key
#         self.secret_key = config.secret_key
#         self.chunk_size = config.chunk

#     # async def connect(self):
#     #     # session = aiobotocore.get_session()
#     #     # self.s3_client = session.create_client(
#     #     #     's3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
#     #     session = aiohttp.ClientSession()
#     #     s3_client = aiobotocore.get_session().create_client(
#     #         's3', region_name='self.region')
#     #     self.s3_client = s3_client

#     async def connect(self):
#         # session = aiohttp.ClientSession()
#         session = get_session()
#         async with session:
#             async with session.create_client(
#                     's3', region_name=self.region,
#                     aws_secret_access_key=self.secret_key,
#                     aws_access_key_id=self.access_key) as s3_client:
#                 self.s3_client = s3_client

#     async def disconnect(self):
#         await self.session.close()
#         await self.s3_client.close()

#     async def poll(self) -> AsyncGenerator[CollectorResult, None]:
#         async with self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.prefix) as response:
#             for obj in response.get('Contents', []):
#                 async with self.download_object(obj['Key']) as file:
#                     async for chunk in self.read_chunks(file):
#                         yield CollectorResult({"object_key": obj['Key'], "chunk": chunk})

#     async def read_chunks(self, file):
#         while True:
#             chunk = await file.read(self.chunk_size)
#             if not chunk:
#                 break
#             yield chunk

#     async def download_object(self, object_key):
#         async with aiofiles.open(object_key, 'wb') as file:
#             await self.s3_client.download_fileobj(self.bucket_name, object_key, file)


# class AWSCollectorFactory(CollectorFactory):
#     def backend(self) -> CollectorBackend:
#         return CollectorBackend.S3

#     def resolve(self, uri: Uri, config: S3CollectConfig) -> Collector:
#         config = S3CollectConfig(bucket='your_bucket_name', region='your_aws_region',
#                                  access_key='your_access_key', secret_key='your_secret_key')
#         return AWSCollector(config)


import asyncio
from typing import AsyncGenerator

import aiofiles
from querent.config.collector_config import CollectorBackend, S3CollectConfig
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.collectors.collector_result import CollectorResult
from querent.common.uri import Uri
import boto3


class AWSCollector(Collector):
    def __init__(self, config: S3CollectConfig):
        self.bucket_name = config.bucket
        self.region = config.region
        self.access_key = config.access_key
        self.secret_key = config.secret_key
        self.chunk_size = config.chunk
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )

    async def connect(self):
        pass  # No asynchronous connection needed for boto3

    async def disconnect(self):
        pass  # No asynchronous disconnect needed for boto3

    async def poll(self) -> AsyncGenerator[CollectorResult, None]:
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=self.prefix)

        for obj in response.get('Contents', []):
            file = self.download_object(obj['Key'])
            async for chunk in self.read_chunks(file):
                yield CollectorResult({"object_key": obj['Key'], "chunk": chunk})

    async def read_chunks(self, file):
        while True:
            chunk = await file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    def download_object(self, object_key):
        file_path = object_key  # Set your desired file path
        self.s3_client.download_file(
            self.bucket_name, object_key, file_path)
        return open(file_path, 'rb')


class AWSCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.S3

    def resolve(self, uri: Uri, config: S3CollectConfig) -> Collector:
        config = S3CollectConfig(bucket='pstreamsbucket1', region='ap-south-1',
                                 access_key='AKIA5ZFZH6CA6LDWIPV5', secret_key='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')
        return AWSCollector(config)
