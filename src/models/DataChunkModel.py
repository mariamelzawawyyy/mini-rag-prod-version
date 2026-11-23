
from bson import ObjectId
from pymongo import InsertOne

from .BaseDataModel import BaseDataModel
from .mongo_db_schemas import DataChunk
from .Enums import DbEnums


# the code responsible for dealing with chunks collection in mongodb
class DataChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DbEnums.COLLECTION_CHUNK_NAME.value]
        # the chunks collection

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        for index in DataChunk.get_indexes():
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"],
            )

    async def insert_data_chunk(self, data_chunk: DataChunk):
        result = await self.collection.insert_one(
            data_chunk.model_dump(
                by_alias=True,
                exclude_none=True
            )
        )
        data_chunk.id = result.inserted_id
        return data_chunk

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            operations = [
                InsertOne(
                    chunk.model_dump(
                        by_alias=True,
                        exclude_none=True
                    )
                )
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)

        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many(
            {"chunk_project_id": project_id}
        )
        return result.deleted_count

    async def delete_chunks_by_asset_id(
        self,
        project_id: ObjectId,
        asset_id: ObjectId
    ):
        result = await self.collection.delete_many(
            {
                "chunk_project_id": project_id,
                "chunk_asset_id": asset_id
            }
        )
        return result.deleted_count
     
    
 
     
 
     

     
 
 