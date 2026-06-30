import os
import random

class RewardManager():
    def __init__(self):
        
        self.rewarddir = os.getcwd() + "/rewards"
        
        

    def redeem_roulette(self):
        # Creates dictionary of folders in rewards, formatted as {Parent folder: [List of files in parent]}
        rewardlist = {}
        rewardtiers = list(os.listdir(self.rewarddir))
        for r in rewardtiers: 
            tierpath = self.rewarddir + "/" + r
            # Checks if folder is empty
            if len(os.listdir(tierpath)) == 0:
                print(f"Folder {r} is empty, skipping")
            else:
                rewarditems = list(os.listdir(tierpath))
                rewardlist[str(r)] = list()

                for i in rewarditems:
                    rewardlist[r].append(i)
                    

        # returns randomly selected file's path from folder structure
        probabilitykeys = []
        for k in rewardlist.keys():
            # Checks if folder name is a number
            try:
                probabilitykeys.append(int(k))
            except:
                print(f"Excluding folder {k}")
        chosenkey = str(random.choices(probabilitykeys, weights=probabilitykeys)[0])
            
        
        return self.rewarddir + "/" + chosenkey + "/" + random.choice(rewardlist[chosenkey])
    

       
            
        
def main():
    print("testing rewards manager")
    reward = RewardManager()
    print(reward.redeem_roulette())

if __name__ == "__main__":
    main()