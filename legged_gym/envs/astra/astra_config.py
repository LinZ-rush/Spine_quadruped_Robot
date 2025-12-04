# # legged_gym/envs/astra/astra_config.py

# from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO


# class AstraFlatCfg(LeggedRobotCfg):
#     class env(LeggedRobotCfg.env):
#         num_envs = 1
#         num_actions = 12      # 策略网络输出 12 个动作 (只控腿)
#         num_observations = 54 # 15(pos)+15(vel)+12(last_action)+3(ang_vel)+3(gravity)+3(cmd)+3(lin_vel) = 54
#                               # 比anymal多了脊柱的3个pos/vel
    
#     class terrain(LeggedRobotCfg.terrain):
#         mesh_type = 'plane'   # 【关键】平地训练模式
#         measure_heights = False # 平地不需要测量高度图

#     class init_state(LeggedRobotCfg.init_state):
#         pos = [0.0, 0.0, 0.40] # 机器人初始位置坐标
        
#         # 关节角度初始值（零位）
#         default_joint_angles = {
#             # --- Front Right  ---
#             'frontbase_FR__j_hip': 0.0, 
#             'FR_hip_FR_j_femur': 0.8, 
#             'FR_femur_FR_j_tibia': -1.5,

#             # --- Front Left ---
#             'frontbase_FL_j_hip': 0.0, 
#             'FL_hip_FL_j_femur': 0.8, 
#             'FL_femur_FL_j_tibia': -1.5,

#             # --- Rear Right ---
#             'backbase_RR_j_hip': 0.0, 
#             'RR_hip_RR_j_femur': 0.8, 
#             'RR_femur_RR_j_tibia': -1.5,

#             # --- Rear Left ---
#             'backbase_RL_j_hip': 0.0, 
#             'RL_hip_RL_j_femur': 0.8, 
#             'RL_femur_RL_j_tibia': -1.5,

#             # --- Spine (Rigid) ---
#             'frontbase_F_j_spine': 0.0,
#             'Dummy_link_Back_k_DU': 0.0,
#             'SPINE_BASE_DU_k_Base': 0.0,
#         }

#     class control(LeggedRobotCfg.control):
#         # PD 参数
#         # 'spine'/'DU'/'Base' 对应脊柱关节，设高刚度以锁定
#         stiffness = {
#             'hip': 10.0, 'femur': 10.0, 'tibia': 10.0,
#             'spine': 1000.0, 'DU': 1000.0, 'Base': 1000.0 
#         }
#         damping = {
#             'hip': 1.0, 'femur': 1.0, 'tibia': 1.0,
#             'spine': 500.0, 'DU': 500.0, 'Base': 500.0
#         }
#         # 动作缩放比例，Anymal通常用0.5，A1用0.25，建议先用0.25保证稳定
#         action_scale = 0.25
#         decimation = 4

#     class asset(LeggedRobotCfg.asset):
#         file = "{LEGGED_GYM_ROOT_DIR}/resources/robots/astra/astra.urdf"
#         name = "astra"
#         foot_name = "tibia" # 只要包含这个字符串的link都被视为脚，用于计算触地
#         penalize_contacts_on = ["femur", "hip", "base", "spine"]
#         terminate_after_contacts_on = ["frontbase", "backbase"]
#         self_collisions = 1 # 1=disable, 0=enable. 初始调试建议禁用自碰撞
#         flip_visual_attachments = False 
#         fix_base_link = False # 设为True时将机器人吊在空中测试关节
    

#     class rewards(LeggedRobotCfg.rewards):
#         # 针对 Flat 地形的奖励微调
#         base_height_target = 0.45
#         max_contact_force = 500.
#         only_positive_rewards = True
        
#         class scales(LeggedRobotCfg.rewards.scales):
#             # 常用奖励权重
#             tracking_lin_vel = 1.0
#             tracking_ang_vel = 0.5
#             lin_vel_z = -2.0
#             ang_vel_xy = -0.05
#             orientation = -0.0
#             torques = -0.00001
#             dof_vel = -0.0
#             dof_acc = -2.5e-7
#             base_height = -0.0 
#             feet_air_time = 1.0
#             collision = -1.0
#             feet_stumble = -0.0 
#             action_rate = -0.005
#             stand_still = -0.0
#             # 额外增加对脊柱运动的惩罚，以防万一
#             dof_pos_limits = -10.0

# class AstraFlatCfgPPO(LeggedRobotCfgPPO):
#     class runner(LeggedRobotCfgPPO.runner):
#         run_name = ''
#         experiment_name = 'flat_astra' # 实验名称
#         max_iterations = 300 # 训练轮数 

# legged_gym/envs/astra/astra_config.py

# from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

# class AstraFlatCfg(LeggedRobotCfg):
#     class env(LeggedRobotCfg.env):
#         num_envs = 1
#         # --- 修改点 1: 动作维度改为 15 (12腿 + 3脊柱) ---
#         num_actions = 15
#         # --- 修改点 2: 观测维度改为 57 ---
#         # 15(pos) + 15(vel) + 15(last_action) + 3(ang_vel) + 3(gravity) + 3(cmd) + 3(lin_vel) = 57
#         num_observations = 57 
    
#     class terrain(LeggedRobotCfg.terrain):
#         mesh_type = 'plane'
#         measure_heights = False

#     class init_state(LeggedRobotCfg.init_state):
#         pos = [0.0, 0.0, 0.42] # 稍微调高一点初始高度，适应脊柱支撑
        
#         default_joint_angles = {
#             # --- Front Right  ---
#             'frontbase_FR__j_hip': 0.0, 
#             'FR_hip_FR_j_femur': 0.0, 
#             'FR_femur_FR_j_tibia': 0.0,

#             # --- Front Left ---
#             'frontbase_FL_j_hip': 0.0, 
#             'FL_hip_FL_j_femur': 0.0, 
#             'FL_femur_FL_j_tibia': 0.0,

#             # --- Rear Right ---
#             'backbase_RR_j_hip': 0.0, 
#             'RR_hip_RR_j_femur': 0.0, 
#             'RR_femur_RR_j_tibia': 0.0,

#             # --- Rear Left ---
#             'backbase_RL_j_hip': 0.0, 
#             'RL_hip_RL_j_femur': 0.0, 
#             'RL_femur_RL_j_tibia': 0.0,

#             # --- Spine (Active) ---
#             'frontbase_F_j_spine': 0.0,
#             'Dummy_link_Back_k_DU': 0.0,
#             'SPINE_BASE_DU_k_Base': 0.0,
#         }

#     class control(LeggedRobotCfg.control):
#         # --- 修改点 3: 降低脊柱刚度 ---
#         # 之前 spine=200 是为了锁定，现在改为 20-40 左右允许控制
#         # 如果发现脊柱太软撑不住躯干，可以适当调大这个值
#         stiffness = {
#             'hip': 10.0, 'femur': 10.0, 'tibia': 10.0,
#             'spine': 20.0, 'DU': 20.0, 'Base': 20.0 
#         }
#         damping = {
#             'hip': 1.0, 'femur': 1.0, 'tibia': 1.0,
#             'spine': 2.0, 'DU': 2.0, 'Base': 2.0
#         }
#         action_scale = 0.5
#         decimation = 4

#     class asset(LeggedRobotCfg.asset):
#         file = "{LEGGED_GYM_ROOT_DIR}/resources/robots/astra/astra.urdf"
#         name = "astra"
#         foot_name = "tibia"
#         # 脊柱部分不再强制终止，允许一定程度的触地（如果在翻滚等动作中）
#         # 但通常脊柱不应触地，保持 penalize
#         penalize_contacts_on = ["femur", "hip", "spine", "DU", "Base"]
#         terminate_after_contacts_on = ["frontbase", "backbase"]
#         self_collisions = 1
#         flip_visual_attachments = False 
#         fix_base_link = False 

#     class rewards(LeggedRobotCfg.rewards):
#         base_height_target = 0.45  
#         max_contact_force = 500.  #最大脚部接触力
#         only_positive_rewards = True
        
#         class scales(LeggedRobotCfg.rewards.scales):
#             tracking_lin_vel = 10.0
#             tracking_ang_vel = 0.5
#             lin_vel_z = -2.0   #惩罚垂直方向线速度，保持稳定
#             ang_vel_xy = -0.05 # 惩罚横滚俯仰角速度
#             orientation = -0.2 # 稍微增加一点方向惩罚，防止脊柱乱扭导致翻车
#             torques = -0.00000 # 略微增加力矩惩罚，鼓励高效使用脊柱
#             dof_vel = -0.0
#             dof_acc = -2.5e-7
#             base_height = -0.0 
#             feet_air_time = 1.0
#             collision = -1.0
#             feet_stumble = -0.0 
#             action_rate = -0.005
#             stand_still = -0.0
            
#             # --- 修改点 4: 移除或调整关节限位惩罚 ---
#             # 惩罚关节位置接近或超过其物理限制
#             dof_pos_limits = -1.0 

# class AstraFlatCfgPPO(LeggedRobotCfgPPO):
#     class runner(LeggedRobotCfgPPO.runner):
#         run_name = ''
#         experiment_name = 'flat_astra_15dof' # 修改实验名以区分
#         max_iterations = 300

# legged_gym/envs/astra/astra_config.py

# legged_gym/envs/astra/astra_config.py

from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

class AstraFlatCfg(LeggedRobotCfg):
    class env(LeggedRobotCfg.env):
        num_envs = 1
        num_actions = 15      # 15个自由度 (12腿 + 3脊柱)
        num_observations = 57 # 57观测维度
    
    class terrain(LeggedRobotCfg.terrain):
        mesh_type = 'plane'
        measure_heights = False

    class init_state(LeggedRobotCfg.init_state):
        pos = [0.0, 0.0, 0.42] 
        
        # 【关键修改】关节名称严格匹配新 URDF
        default_joint_angles = {
            # --- Front Left (连接 Frontpart) ---
            'Frontpart_FL_j_hip': 0.0, 
            'FL_hip_FL_j_femur': -0.4, 
            'FL_femur_FL_j_tibia': 0.8,

            # --- Front Right (连接 Frontpart) ---
            'Frontpart_FR_j_hip': 0.0, 
            'FR_hip_FR_j_femur': -0.4, 
            'FR_femur_FR_j_tibia': 0.8,

            # --- Rear Left (连接 Backpart) ---
            'Backpart_RL_j_hip': 0.0, 
            'RL_hip_RL_j_femur': -0.4, 
            'RL_femur_RL_j_tibia': 0.8,

            # --- Rear Right (连接 Backpart) ---
            'Backpart_RR_j_hip': 0.0, 
            'RR_hip_RR_j_femur': -0.4, 
            'RR_femur_RR_j_tibia': 0.8,

            # --- Spine / Body Joints ---
            # 连接脊柱与前躯干: Spine -> Frontpart
            'Spine_Front_j_Spine': 0.0,
            # 连接基座与后躯干: Base_link -> Backpart
            'Base_link_Back_j_Base': 0.0,
            # 连接基座与脊柱: Base_link -> Spine
            'Base_link_Spine_j_Base': 0.0,
        }

    class control(LeggedRobotCfg.control):
        # 刚度设置 (使用正则匹配关节名)
        # 'hip', 'femur', 'tibia' 匹配腿部关节
        # 'Spine' -> 匹配 'Spine_Front_j_Spine' 和 'Base_link_Spine_j_Base'
        # 'Base'  -> 匹配 'Base_link_Back_j_Base'
        stiffness = {
            'hip': 20.0, 'femur': 20.0, 'tibia': 20.0,
            'Spine': 40.0, 'Base': 40.0 
        }
        damping = {
            'hip': 1.0, 'femur': 1.0, 'tibia': 1.0,
            'Spine': 2.0, 'Base': 2.0
        }
        action_scale = 0.25
        decimation = 4

    class asset(LeggedRobotCfg.asset):
        file = "{LEGGED_GYM_ROOT_DIR}/resources/robots/astra/astra.urdf"
        name = "astra"
        foot_name = "tibia" 
        
        # 接触惩罚部件 (Link Names)
        # 匹配 URDF 中的 Link 名称
        penalize_contacts_on = ["femur", "hip", "Spine", "Base_link", "Frontpart", "Backpart"]
        terminate_after_contacts_on = ["Frontpart", "Backpart"]
        self_collisions = 1
        flip_visual_attachments = False 
        fix_base_link = False 

    class rewards(LeggedRobotCfg.rewards):
        base_height_target = 0.45  
        max_contact_force = 500.
        only_positive_rewards = True
        
        class scales(LeggedRobotCfg.rewards.scales):
            tracking_lin_vel = 1.0 
            tracking_ang_vel = 0.5
            lin_vel_z = -2.0
            ang_vel_xy = -0.05 
            orientation = -0.2 
            torques = -0.00002 
            dof_vel = -0.0
            dof_acc = -2.5e-7
            base_height = -0.0 
            feet_air_time = 1.0
            collision = -1.0
            feet_stumble = -0.0 
            action_rate = -0.005
            stand_still = -0.0
            dof_pos_limits = -1.0 

class AstraFlatCfgPPO(LeggedRobotCfgPPO):
    class runner(LeggedRobotCfgPPO.runner):
        run_name = ''
        experiment_name = 'flat_astra_15dof' 
        max_iterations = 300