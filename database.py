import sqlite3
from pathing import DATABASE_PATH

class DatabaseManager(): 
    def __init__(self): 
        
        self.con = sqlite3.connect(DATABASE_PATH)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS Redeems(ID INTEGER PRIMARY KEY AUTOINCREMENT, ChatterName varchar(255), ChatterID INTEGER, RewardName varchar(255), RewardTier int, RewardPath varchar(255), Timestamp TEXT DEFAULT CURRENT_TIMESTAMP) ")

    def new_entry(self, entry):
        self.cur.execute("INSERT INTO Redeems (ChatterName, ChatterID, RewardName, RewardTier, RewardPath) VALUES (:chatter_name, :chatter_id, :reward_name, :reward_tier, :reward_path)", entry)
        self.con.commit()

    def get_rewards(self, chatterID):
        
        req1 = self.cur.execute("SELECT ChatterName, ChatterID, RewardName, RewardTier, RewardPath, COUNT(*) AS CountOfRedeems FROM Redeems WHERE ChatterID = :chatter_id GROUP BY RewardPath" , {"chatter_id": chatterID})
        columns = [column[0] for column in req1.description]
        previous_rewards = []
        for r in req1.fetchall():
            old_reward = dict(zip(columns, r))
            previous_rewards.append(old_reward)


        return previous_rewards

    def close_database(self):
        self.con.close()


    
def test():
    database = DatabaseManager()
    data = {"chatter_name": "TestUser", "chatter_id": 1234, "reward_name": "RewardTest2", "reward_tier": 321, "reward_path": "./rewards/321/RewardTest2.jpg"}
    database.new_entry(data)
    print(database.get_rewards(1234))

if __name__ == "__main__":
    test()
