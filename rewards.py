import os
import random
from errors import MissingRewardFolderException

class RewardManager():
    def __init__(self):
        
        self.rewarddir = os.getcwd() + "/display/rewards/"
        
        
    def get_reward_tiers(self):
        # returns sorted list of reward tiers
        try:
            reward_folders = list(os.listdir(self.rewarddir))
        except FileNotFoundError as e:
            print("Creating rewards folder and example folders")
            try: 
                os.mkdir("./display/rewards")
                os.mkdir("./display/rewards/10")
                os.mkdir("./display/rewards/50")
                os.mkdir("./display/rewards/75")
            except OSError as e:
                print("Unable to create rewards folders")
                raise Exception("Unable to create rewards folders") from e
            raise MissingRewardFolderException(
            "Missing parent reward folder. Please add reward items to sub folders within the new ./rewards folder"
            ) from e 
            
        reward_tiers = []
        for rt in reward_folders:
            if len(os.listdir(self.rewarddir + "/" + rt)) == 0:
                print(f"Folder {rt} is empty, skipping")
            else:
                try:
                    reward_tiers.append(int(rt))
                except:
                    print(f"Folder {rt} is not a number, skipping")
        if len(reward_tiers) == 0:
            print("No numerical reward folders detected. Verify that the rewards are in the correct folder")
            return None

        reward_tiers.sort()

        print(f"reward tiers: {reward_tiers}")
        return reward_tiers
        

    def redeem_roulette(self):
                   
        # returns randomly selected file's path from folder structure
        try:
            probabilitykeys = self.get_reward_tiers()
        except MissingRewardFolderException as e:
            print(f"Folder error: {e}")
            return
        if probabilitykeys == None:
            return None

        fallback_tier = probabilitykeys[len(probabilitykeys) - 1]
        
        chosen_tier = fallback_tier
        for k in probabilitykeys:
            
            if (k >= random.randrange(1, 101, 1)):
                chosen_tier = k
                break

        chosen_reward = random.choice(os.listdir(self.rewarddir + "/" + str(chosen_tier)))
        reward_path = "./rewards/" + str(chosen_tier) + "/" + chosen_reward
        
        return {"reward_path": reward_path, "reward_tier": chosen_tier, "reward_name": chosen_reward.split(".")[0]}
    

            
        
def main():
    print("testing rewards manager")
    reward = RewardManager()
    print(reward.redeem_roulette())

if __name__ == "__main__":
    main()