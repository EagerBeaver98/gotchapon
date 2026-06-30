import os
import random

rewarddir = os.getcwd() + "/rewards"
class RewardManager():
    def __init__(self, config):
        # Creates dictionary of folders in rewards, formatted as {Parent folder: [List of files in parent]}
        self.rewardlist = {}
        self.rewardtiers = list(os.listdir(rewarddir))
        for r in self.rewardtiers:
            rewarditems = list(os.listdir(rewarddir + "/" + r))

            self.rewardlist[str(r)] = list()

            for i in rewarditems:
                self.rewardlist[r].append(i)

    def redeemRoulette(self):
        # returns randomly selected file's path from folder structure
        probabilitykeys = []
        for k in self.rewardlist.keys():
            probabilitykeys.append(int(k))
        chosenkey = str(random.choices(probabilitykeys, weights=probabilitykeys)[0])
        return rewarddir + chosenkey + "/" + random.choice(self.rewardlist[chosenkey])
    

       
            
        
def main():
    print("testing rewards manager")
    reward = RewardManager("test")
    print(reward.redeemRoulette())

if __name__ == "__main__":
    main()