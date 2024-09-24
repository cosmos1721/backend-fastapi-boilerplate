from db.mongoEngine import mongo_user, mongo_data

user_collection = 'user-data'
data_collection = 'game-details'
waitlist_table_collection = 'waitlist-table'

async def verify_id(id, usage: str= 'user_id') -> bool:
    if usage == 'user_id':
        projection = {
            "user_id": 1
        }
        existing_user = await mongo_user[user_collection].find_one({"user_id": id}, projection) and await mongo_user[waitlist_table_collection].find_one({"user_id": id}, projection)
        if existing_user:
            return True
    elif usage == 'game':
        projection = {
            "game_id": 1
        }
        existing_id = await mongo_data[data_collection].find_one({"game_id": id}, projection)
        if existing_id:
            return True
    elif usage == 'project_id':
        projection = {
            "project_id": 1
        }
        existing_project = await mongo_data[data_collection].find_one({"project_id": id}, projection)
        if existing_project:
            return True
    return False