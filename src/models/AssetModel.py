from typing import Optional
from bson import ObjectId
from .BaseDataModel import BaseDataModel
from .mongo_db_schemas import Asset
from .Enums import DbEnums
 
  
class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DbEnums.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        for index in Asset.get_indexes():
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"],
            )

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(
            asset.model_dump(by_alias=True, exclude_none=True)
        )
        asset.id = result.inserted_id
        return asset

    async def get_all_project_assets(
        self,
        asset_project_id: ObjectId,
        asset_type: Optional[str] = None,
    ):
        if isinstance(asset_project_id, str):
            asset_project_id = ObjectId(asset_project_id)

        query = {"asset_project_id": asset_project_id}
        if asset_type:
            query["asset_type"] = asset_type

        records = await self.collection.find(query).to_list(length=None)
        return [Asset(**record) for record in records]

    async def get_asset_record(
        self,
        asset_project_id: ObjectId,
        file_id : str  
    ):
        record = await self.collection.find_one(
            {
                "asset_project_id": asset_project_id,
                "asset_name" : file_id 
            }
        )
        return Asset(**record) if record else None 
  

     


