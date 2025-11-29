# astra/astra_robot.py
from legged_gym.envs.base.legged_robot import LeggedRobot

class AstraRobot(LeggedRobot):
    # 重写你需要修改的函数
    def _reward_spine_motion(self):
        # 写你自己的脊柱奖励逻辑
        pass