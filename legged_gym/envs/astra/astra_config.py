from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

class AstraRoughCfg(LeggedRobotCfg):
    class init_state(LeggedRobotCfg.init_state):
        # 这里设置初始关节角度
        # Fusion 导出时通常腿是垂直向下的，这里建议给一点弯曲，避免奇异点
        pos = {
            'hip': 0.0,
            'thigh': 0.8,  # 大腿关节
            'calf': -1.5,  # 膝盖关节
            'spine': 0.0   # 脊柱关节
        }
        # 初始位置和速度
        default_joint_angles = pos
        
    class control(LeggedRobotCfg.control):
        # PD 控制器参数 (论文数据来源)
        # 论文 P42 提到 MIT 模式示例使用了 Kp=6.0, Kd=0.6 
        # 你可以根据关节不同分别设置，注意膝关节有 1.5 倍减速比 
        stiffness = {'joint': 6.0}  # P gain
        damping = {'joint': 0.6}    # D gain
        
        # 动作缩放比例 (Action Scale)
        action_scale = 0.25
        decimation = 4

    class asset(LeggedRobotCfg.asset):
        file = '{LEGGED_GYM_ROOT_DIR}/resources/robots/astra/astra.urdf'
        name = "astra"
        foot_name = "foot" # 对应你 URDF 里脚部 link 的名字
        penalize_contacts_on = ["thigh", "calf"]
        terminate_after_contacts_on = ["base"]
        self_collisions = 1 # 开启自碰撞检测
        flip_visual_attachments = False # 如果模型显示反了，改这个

    class domain_rand(LeggedRobotCfg.domain_rand):
        randomize_friction = True
        friction_range = [0.5, 1.25]
        randomize_base_mass = True
        added_mass_range = [-1.0, 1.0] # 论文提到整机约 9.5kg，这里允许随机扰动

class AstraRoughCfgPPO(LeggedRobotCfgPPO):
    class runner(LeggedRobotCfgPPO.runner):
        run_name = 'astra_rough'
        experiment_name = 'astra_rough'