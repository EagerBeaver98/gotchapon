import sqlite3


class DatabaseManager(): 
    def __init__(self): 
        
        self.con = sqlite3.connect('redeems.db')
        self.cur = self.con.cursor()
        res = self.cur.execute("SELECT name FROM sqlite_master WHERE name='Redeems'")
        if res.fetchone() is None:
            self.cur.execute("CREATE TABLE Redeems(ID INTEGER PRIMARY KEY AUTOINCREMENT, ChatterName varchar(255), ChatterID INTEGER, RewardName varchar(255), RewardTier int, Timestamp TEXT DEFAULT CURRENT_TIMESTAMP) ")

    def new_entry(self, entry):
        res = self.cur.execute("Select ChatterID FROM Redeems WHERE ChatterID = :chatter_id AND RewardName = :reward_name AND RewardTier = :reward_tier" , {"chatter_id": entry["chatter_id"], "reward_name": entry["reward_name"], "reward_tier": entry["reward_tier"]})
        if res.fetchone() is None: 
            self.cur.execute("INSERT INTO Redeems (ChatterName, ChatterID, RewardName, RewardTier) VALUES (:chatter_name, :chatter_id, :reward_name, :reward_tier)", entry)
            self.con.commit()

    def get_rewards(self, chatterID):
        req = self.cur.execute("SELECT * FROM Redeems WHERE ChatterID = :chatter_id", {"chatter_id": chatterID})
        return req.fetchall()

    
def test():
    database = DatabaseManager()
    data = {"chatter_name": "TestUser", "chatter_id": 1234, "reward_name": "RewardTest2", "reward_tier": 321}
    database.new_entry(data)
    print(database.get_rewards(1234))

if __name__ == "__main__":
    test()
