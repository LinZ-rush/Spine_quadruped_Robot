# legged_gym/envs/astra/astra_config.py

from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

class AstraFlatCfg(LeggedRobotCfg):
    class env(LeggedRobotCfg.env):
        num_envs = 1
        num_actions = 15      # 15个自由度 (12腿 + 3脊柱)
        num_observations = 57 # 57观测维度（15pos + 15vel + 15last_action + 3ang_vel + 3lin_vel + 3cmd+ 3gravity）
    
    class terrain(LeggedRobotCfg.terrain):
        mesh_type = 'plane'
        measure_heights = False

    class init_state(LeggedRobotCfg.init_state):
        pos = [0.0, 0.0, 0.42] 
        
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
        
        # 接触惩罚部件 (匹配 URDF 中的 Link 名称)
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
            lin_vel_z = -2.0 #惩罚垂直方向线速度，保持纵向稳定
            ang_vel_xy = -0.05 # 惩罚横滚和俯仰角速度
            orientation = -0.2 
            torques = -0.00002 #增加力矩惩罚，鼓励高校使用脊柱节能
            dof_vel = -0.0
            dof_acc = -2.5e-7
            base_height = -0.0 
            feet_air_time = 1.0
            collision = -1.0
            feet_stumble = -0.0 
            action_rate = -0.005
            stand_still = -0.0
            dof_pos_limits = -1.0 #惩罚关节位置超出限制

class AstraFlatCfgPPO(LeggedRobotCfgPPO):
    class runner(LeggedRobotCfgPPO.runner):
        run_name = ''
        experiment_name = 'astra_flat' 
        max_iterations = 300