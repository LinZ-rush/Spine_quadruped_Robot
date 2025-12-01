# legged_gym/envs/astra/astra_config.py

from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO


class AstraFlatCfg(LeggedRobotCfg):
    class env(LeggedRobotCfg.env):
        num_envs = 1
        num_actions = 12      # 策略网络输出 12 个动作 (只控腿)
        num_observations = 54 # 15(pos)+15(vel)+12(last_action)+3(ang_vel)+3(gravity)+3(cmd)+3(lin_vel) = 54
                              # 比anymal多了脊柱的3个pos/vel
    
    class terrain(LeggedRobotCfg.terrain):
        mesh_type = 'plane'   # 【关键】平地训练模式
        measure_heights = False # 平地不需要测量高度图

    class init_state(LeggedRobotCfg.init_state):
        pos = [0.0, 0.0, 0.40] # 机器人初始位置坐标
        
        # 关节角度初始值（零位）
        default_joint_angles = {
            # --- Front Right  ---
            'frontbase_FR__j_hip': 0.0, 
            'FR_hip_FR_j_femur': 0.8, 
            'FR_femur_FR_j_tibia': -1.5,

            # --- Front Left ---
            'frontbase_FL_j_hip': 0.0, 
            'FL_hip_FL_j_femur': 0.8, 
            'FL_femur_FL_j_tibia': -1.5,

            # --- Rear Right ---
            'backbase_RR_j_hip': 0.0, 
            'RR_hip_RR_j_femur': 0.8, 
            'RR_femur_RR_j_tibia': -1.5,

            # --- Rear Left ---
            'backbase_RL_j_hip': 0.0, 
            'RL_hip_RL_j_femur': 0.8, 
            'RL_femur_RL_j_tibia': -1.5,

            # --- Spine (Rigid) ---
            'frontbase_F_j_spine': 0.0,
            'Dummy_link_Back_k_DU': 0.0,
            'SPINE_BASE_DU_k_Base': 0.0,
        }

    class control(LeggedRobotCfg.control):
        # PD 参数
        # 'spine'/'DU'/'Base' 对应脊柱关节，设高刚度以锁定
        stiffness = {
            'hip': 10.0, 'femur': 10.0, 'tibia': 10.0,
            'spine': 200.0, 'DU': 200.0, 'Base': 200.0 
        }
        damping = {
            'hip': 1.0, 'femur': 1.0, 'tibia': 1.0,
            'spine': 5.0, 'DU': 5.0, 'Base': 5.0
        }
        # 动作缩放比例，Anymal通常用0.5，A1用0.25，建议先用0.25保证稳定
        action_scale = 0.5
        decimation = 4

    class asset(LeggedRobotCfg.asset):
        file = "{LEGGED_GYM_ROOT_DIR}/resources/robots/astra/astra.urdf"
        name = "astra"
        foot_name = "tibia" # 只要包含这个字符串的link都被视为脚，用于计算触地
        penalize_contacts_on = ["femur", "hip", "base", "spine"]
        terminate_after_contacts_on = ["frontbase", "backbase"]
        self_collisions = 1 # 1=disable, 0=enable. 初始调试建议禁用自碰撞
        flip_visual_attachments = False 
        fix_base_link = False # 设为True时将机器人吊在空中测试关节
        

    class rewards(LeggedRobotCfg.rewards):
        # 针对 Flat 地形的奖励微调
        base_height_target = 0.45
        max_contact_force = 500.
        only_positive_rewards = True
        
        class scales(LeggedRobotCfg.rewards.scales):
            # 常用奖励权重
            tracking_lin_vel = 1.0
            tracking_ang_vel = 0.5
            lin_vel_z = -2.0
            ang_vel_xy = -0.05
            orientation = -0.0
            torques = -0.00001
            dof_vel = -0.0
            dof_acc = -2.5e-7
            base_height = -0.0 
            feet_air_time = 1.0
            collision = -1.0
            feet_stumble = -0.0 
            action_rate = -0.005
            stand_still = -0.0
            # 额外增加对脊柱运动的惩罚，以防万一
            dof_pos_limits = -10.0

class AstraFlatCfgPPO(LeggedRobotCfgPPO):
    class runner(LeggedRobotCfgPPO.runner):
        run_name = ''
        experiment_name = 'flat_astra' # 实验名称
        max_iterations = 300 # 训练轮数