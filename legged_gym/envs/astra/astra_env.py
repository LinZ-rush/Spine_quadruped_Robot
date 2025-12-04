# # legged_gym/envs/astra/astra_env.py

# from legged_gym.envs.base.legged_robot import LeggedRobot
# from isaacgym import gymtorch, gymapi
# import torch
# from .astra_config import AstraFlatCfg

# class AstraRobot(LeggedRobot):
#     cfg: AstraFlatCfg

#     def _init_buffers(self):
#         # ==========================================================
#         # 1. 【核心修复】 防止父类初始化时 crash
#         # ==========================================================
#         # 备份真实的动作维度 (12)
#         original_num_actions = self.num_actions
        
#         # 临时将 num_actions 设为 num_dof (15)
#         # 这样父类在初始化 p_gains/d_gains/torques 时就会创建 15 维的数组
#         # 从而在遍历 15 个关节赋 PD 值时不会报 IndexError
#         self.num_actions = self.num_dof
        
#         # 安全调用父类初始化
#         super()._init_buffers()

#         # ==========================================================
#         # 2. 【还原设置】 将维度改回 12 以适配 RL 策略
#         # ==========================================================
#         self.num_actions = original_num_actions
        
#         # 重新初始化 actions 和 last_actions 为 12 维
#         # (因为刚才父类把它们初始化成了 15 维)
#         self.actions = torch.zeros(self.num_envs, self.num_actions, dtype=torch.float, device=self.device, requires_grad=False)
#         self.last_actions = torch.zeros(self.num_envs, self.num_actions, dtype=torch.float, device=self.device, requires_grad=False)
        
#         # 注意：self.torques, self.p_gains, self.d_gains 此时保留为 15 维
#         # 这正是我们想要的！(物理引擎需要 15 维力矩，计算过程也需要 15 维 PD)

#         # ==========================================================
#         # 3. 识别关节索引
#         # ==========================================================
#         self.spine_keywords = ["spine", "DU", "Base"]
#         self.spine_dof_indices = torch.tensor([i for i, name in enumerate(self.dof_names) if any(k in name for k in self.spine_keywords)], device=self.device, dtype=torch.long)
#         self.leg_dof_indices = torch.tensor([i for i in range(self.num_dofs) if i not in self.spine_dof_indices.tolist()], device=self.device, dtype=torch.long)
        
    
#     def _pre_physics_step(self, actions):
#         self.actions = actions.clone()
        
#         # 1. 扩展 actions (12) -> (15)
#         actions_scaled = actions * self.cfg.control.action_scale
#         expanded_actions = torch.zeros(self.num_envs, self.num_dof, device=self.device)
#         expanded_actions[:, self.leg_dof_indices] = actions_scaled
        
#         # 2. 计算目标位置 (脊柱部分为 0，即保持默认)
#         targets = self.default_dof_pos + expanded_actions
        
#         # 3. 强制锁定脊柱目标
#         targets[:, self.spine_dof_indices] = self.default_dof_pos[:, self.spine_dof_indices]

#         # 发送目标
#         self.gym.set_dof_position_target_tensor(self.sim, gymtorch.unwrap_tensor(targets))

#     def _compute_torques(self, actions):
#         # 1. 扩展 actions (12) -> (15)
#         actions_scaled = actions * self.cfg.control.action_scale
#         expanded_actions = torch.zeros(self.num_envs, self.num_dof, device=self.device)
#         expanded_actions[:, self.leg_dof_indices] = actions_scaled
        
#         # 2. 计算 15 维 PD 力矩
#         control_type = self.cfg.control.control_type
#         if control_type == "P":
#             target_pos = self.default_dof_pos + expanded_actions
#             torques = self.p_gains * (target_pos - self.dof_pos) - self.d_gains * self.dof_vel
#         else:
#             torques = torch.zeros_like(self.dof_pos)
            
#         return torques

#     def _get_noise_scale_vec(self, cfg):
#         # 重写此函数以解决父类针对 12 DoF 硬编码索引的问题
#         noise_vec = torch.zeros_like(self.obs_buf[0])
#         self.add_noise = self.cfg.noise.add_noise
#         noise_scales = self.cfg.noise.noise_scales
#         noise_level = self.cfg.noise.noise_level
        
#         # 基础状态噪声
#         noise_vec[:3] = noise_scales.lin_vel * noise_level * self.obs_scales.lin_vel
#         noise_vec[3:6] = noise_scales.ang_vel * noise_level * self.obs_scales.ang_vel
#         noise_vec[6:9] = noise_scales.gravity * noise_level
#         noise_vec[9:12] = 0. # commands
        
#         # 动态计算关节索引范围 (适配 15 DoF)
#         dof_pos_start = 12
#         dof_pos_end = 12 + self.num_dof
#         dof_vel_start = dof_pos_end
#         dof_vel_end = dof_vel_start + self.num_dof
        
#         noise_vec[dof_pos_start:dof_pos_end] = noise_scales.dof_pos * noise_level * self.obs_scales.dof_pos
#         noise_vec[dof_vel_start:dof_vel_end] = noise_scales.dof_vel * noise_level * self.obs_scales.dof_vel
        
#         # 上一次动作噪声
#         action_start = dof_vel_end
#         action_end = action_start + self.num_actions
#         noise_vec[action_start:action_end] = 0. # previous actions
        
#         if self.cfg.terrain.measure_heights:
#             noise_vec[action_end:action_end+187] = noise_scales.height_measurements* noise_level * self.obs_scales.height_measurements
            
#         return noise_vec
    
#     # --- 🛠️ 调试专用函数：打印关节角度 (度数) ---
#     def debug_print_joint_angles(self):
#         import time
#         # 限制打印频率，每 1 秒打印一次，避免刷屏
#         if not hasattr(self, 'last_print_time'):
#             self.last_print_time = 0
        
#         current_time = time.time()
#         if current_time - self.last_print_time < 1.0:
#             return
        
#         self.last_print_time = current_time

#         print("\n" + "="*60)
#         print(f"{'Joint Name':<30} | {'Config(Deg)':<12} | {'Current(Deg)':<12}")
#         print("-" * 60)
        
#         # 获取张量数据并转为 CPU numpy 数组
#         current_pos_rad = self.dof_pos[0, :].cpu().numpy() # 取第0个环境
#         default_pos_rad = self.default_dof_pos[0, :].cpu().numpy()
        
#         for i, name in enumerate(self.dof_names):
#             # 弧度转度数
#             current_deg = current_pos_rad[i] * 180 / 3.14159
#             default_deg = default_pos_rad[i] * 180 / 3.14159
            
#             # 打印，保留1位小数
#             print(f"[{i:02d}] {name:<25} | {default_deg:>10.1f} | {current_deg:>10.1f}")
            
#         print("="*60 + "\n")

#         # ... (接在 debug_print_joint_angles 函数后面)

#     def step(self, actions):
#         # 1. 调用父类原本的 step 逻辑 (物理模拟、计算奖励、重置环境等)
#         #    这样我们不需要自己重写复杂的物理循环
#         obs, privileged_obs, rew, reset, extras = super().step(actions)
        
#         # 2. 【插入调试】在物理步结束后，打印当前的关节角度
#         #    这将调用上面定义的 debug_print_joint_angles
#         self.debug_print_joint_angles()
        
#         # 3. 返回父类计算的结果
#         return obs, privileged_obs, rew, reset, extras
    
# legged_gym/envs/astra/astra_env.py

# legged_gym/envs/astra/astra_env.py

# from legged_gym.envs.base.legged_robot import LeggedRobot
# from isaacgym import gymtorch, gymapi
# import torch
# from .astra_config import AstraFlatCfg

# class AstraRobot(LeggedRobot):
#     cfg: AstraFlatCfg

#     def _init_buffers(self):
#         # [已修复] 移除 12-DOF 时的维度 Hack，直接使用父类初始化 15 维 buffers
#         super()._init_buffers()
        
#         # 移除脊柱索引识别逻辑，不再需要将动作分开处理。
#         # self.spine_keywords = ...
        
    
#     def _pre_physics_step(self, actions):
#         self.actions = actions.clone()
        
#         # 🐛 修复：使用 self.cfg.control.action_scale
#         actions_scaled = actions * self.cfg.control.action_scale 
        
#         # 目标位置 = 初始角度 + 策略输出的相对变化
#         targets = self.default_dof_pos + actions_scaled
        
#         # 发送目标
#         self.gym.set_dof_position_target_tensor(self.sim, gymtorch.unwrap_tensor(targets))

#     def _compute_torques(self, actions):
#         # 🐛 修复：使用 self.cfg.control.action_scale
#         actions_scaled = actions * self.cfg.control.action_scale
        
#         control_type = self.cfg.control.control_type
#         if control_type == "P":
#             target_pos = self.default_dof_pos + actions_scaled
#             torques = self.p_gains * (target_pos - self.dof_pos) - self.d_gains * self.dof_vel
#         else:
#             torques = torch.zeros_like(self.dof_pos)
            
#         return torques

#     def _get_noise_scale_vec(self, cfg):
#         # [已更新] 修正以适配 15 DoF (57 维观测)
#         noise_vec = torch.zeros_like(self.obs_buf[0])
#         self.add_noise = self.cfg.noise.add_noise
#         noise_scales = self.cfg.noise.noise_scales
#         noise_level = self.cfg.noise.noise_level
        
#         # 基础状态噪声 (3+3+3+3 = 12 维)
#         noise_vec[:3] = noise_scales.lin_vel * noise_level * self.obs_scales.lin_vel
#         noise_vec[3:6] = noise_scales.ang_vel * noise_level * self.obs_scales.ang_vel
#         noise_vec[6:9] = noise_scales.gravity * noise_level
#         noise_vec[9:12] = 0. # commands
        
#         # DOF Pos/Vel/Actions 都是 15 维
#         dof_pos_start = 12
#         dof_pos_end = dof_pos_start + self.num_dof # 27
#         dof_vel_start = dof_pos_end
#         dof_vel_end = dof_vel_start + self.num_dof # 42
        
#         noise_vec[dof_pos_start:dof_pos_end] = noise_scales.dof_pos * noise_level * self.obs_scales.dof_pos
#         noise_vec[dof_vel_start:dof_vel_end] = noise_scales.dof_vel * noise_level * self.obs_scales.dof_vel
        
#         # 上一次动作噪声
#         action_start = dof_vel_end
#         action_end = action_start + self.num_actions # 57
#         noise_vec[action_start:action_end] = 0. # previous actions
        
#         if self.cfg.terrain.measure_heights:
#             noise_vec[action_end:action_end+187] = noise_scales.height_measurements* noise_level * self.obs_scales.height_measurements
            
#         return noise_vec
    
#     # 保留调试函数
#     def debug_print_joint_angles(self):
#         import time
#         if not hasattr(self, 'last_print_time'):
#             self.last_print_time = 0
        
#         current_time = time.time()
#         if current_time - self.last_print_time < 1.0:
#             return
        
#         self.last_print_time = current_time

#         # --- 修改表头：增加 Target 列 ---
#         print("\n" + "="*75)
#         # Config = 静态零点, Target = 动态指令, Current = 实际位置
#         print(f"{'Joint Name':<25} | {'Config':<8} | {'Target':<8} | {'Current':<8}")
#         print("-" * 75)
        
#         # 获取数据
#         current_pos = self.dof_pos[0, :].cpu().numpy()
#         default_pos = self.default_dof_pos[0, :].cpu().numpy()
        
#         # --- 新增：计算当前的动态目标 Target ---
#         # Target = Default + Action * Scale
#         # 注意：这里取第0个环境的 action
#         if hasattr(self, 'actions'):
#              # 获取当前策略输出的动作
#             actions = self.actions[0, :].cpu().numpy()
#             scale = self.cfg.control.action_scale
#             target_pos = default_pos + actions * scale
#         else:
#             target_pos = default_pos # 如果还没开始step，暂时等于default

#         for i, name in enumerate(self.dof_names):
#             # 弧度转度数
#             c_deg = default_pos[i] * 180 / 3.14159
#             t_deg = target_pos[i] * 180 / 3.14159  # 动态目标
#             a_deg = current_pos[i] * 180 / 3.14159 # 实际位置
            
#             # 打印三列数据
#             print(f"[{i:02d}] {name:<22} | {c_deg:>8.1f} | {t_deg:>8.1f} | {a_deg:>8.1f}")
            
#         print("="*75 + "\n")


#     def step(self, actions):
#         obs, privileged_obs, rew, reset, extras = super().step(actions)
#         self.debug_print_joint_angles() 
#         return obs, privileged_obs, rew, reset, extras
# legged_gym/envs/astra/astra_env.py

# legged_gym/envs/astra/astra_env.py

from legged_gym.envs.base.legged_robot import LeggedRobot
from isaacgym import gymtorch, gymapi
import torch
from .astra_config import AstraFlatCfg

class AstraRobot(LeggedRobot):
    cfg: AstraFlatCfg

    def _init_buffers(self):
        # 直接使用父类初始化 15 维 buffers
        super()._init_buffers()
        
        # --------------------------------------------------------
        # 注意：关节索引逻辑已更新为适配新 URDF
        # 如果未来需要手动锁定脊柱，请参考以下名称：
        # - "Spine_Front_j_Spine"
        # - "Base_link_Back_j_Base"
        # - "Base_link_Spine_j_Base"
        # --------------------------------------------------------
    
    def _pre_physics_step(self, actions):
        self.actions = actions.clone()
        
        # 使用配置中的缩放比例
        actions_scaled = actions * self.cfg.control.action_scale 
        
        # 目标位置 = 初始角度 + 策略输出的相对变化
        # 涵盖所有 15 个关节 (12腿 + 3脊柱)
        targets = self.default_dof_pos + actions_scaled
        
        # 发送目标
        self.gym.set_dof_position_target_tensor(self.sim, gymtorch.unwrap_tensor(targets))

    def _compute_torques(self, actions):
        actions_scaled = actions * self.cfg.control.action_scale
        
        control_type = self.cfg.control.control_type
        if control_type == "P":
            target_pos = self.default_dof_pos + actions_scaled
            torques = self.p_gains * (target_pos - self.dof_pos) - self.d_gains * self.dof_vel
        else:
            torques = torch.zeros_like(self.dof_pos)
            
        return torques

    def _get_noise_scale_vec(self, cfg):
        # 适配 15 DoF (57 维观测)
        noise_vec = torch.zeros_like(self.obs_buf[0])
        self.add_noise = self.cfg.noise.add_noise
        noise_scales = self.cfg.noise.noise_scales
        noise_level = self.cfg.noise.noise_level
        
        # 基础状态噪声
        noise_vec[:3] = noise_scales.lin_vel * noise_level * self.obs_scales.lin_vel
        noise_vec[3:6] = noise_scales.ang_vel * noise_level * self.obs_scales.ang_vel
        noise_vec[6:9] = noise_scales.gravity * noise_level
        noise_vec[9:12] = 0. # commands
        
        # DOF 噪声索引范围 (适配 15 DoF)
        dof_pos_start = 12
        dof_pos_end = dof_pos_start + self.num_dof # 27
        dof_vel_start = dof_pos_end
        dof_vel_end = dof_vel_start + self.num_dof # 42
        
        noise_vec[dof_pos_start:dof_pos_end] = noise_scales.dof_pos * noise_level * self.obs_scales.dof_pos
        noise_vec[dof_vel_start:dof_vel_end] = noise_scales.dof_vel * noise_level * self.obs_scales.dof_vel
        
        # 上一次动作噪声
        action_start = dof_vel_end
        action_end = action_start + self.num_actions # 57
        noise_vec[action_start:action_end] = 0. # previous actions
        
        if self.cfg.terrain.measure_heights:
            noise_vec[action_end:action_end+187] = noise_scales.height_measurements* noise_level * self.obs_scales.height_measurements
            
        return noise_vec
    
    # 调试函数
    def debug_print_joint_angles(self):
        import time
        if not hasattr(self, 'last_print_time'):
            self.last_print_time = 0
        
        current_time = time.time()
        if current_time - self.last_print_time < 1.0:
            return
        
        self.last_print_time = current_time

        print("\n" + "="*75)
        print(f"{'Joint Name':<25} | {'Config':<8} | {'Target':<8} | {'Current':<8}")
        print("-" * 75)
        
        current_pos = self.dof_pos[0, :].cpu().numpy()
        default_pos = self.default_dof_pos[0, :].cpu().numpy()
        
        if hasattr(self, 'actions'):
            actions = self.actions[0, :].cpu().numpy()
            scale = self.cfg.control.action_scale
            target_pos = default_pos + actions * scale
        else:
            target_pos = default_pos 

        for i, name in enumerate(self.dof_names):
            c_deg = default_pos[i] * 180 / 3.14159
            t_deg = target_pos[i] * 180 / 3.14159
            a_deg = current_pos[i] * 180 / 3.14159
            
            print(f"[{i:02d}] {name:<22} | {c_deg:>8.1f} | {t_deg:>8.1f} | {a_deg:>8.1f}")
            
        print("="*75 + "\n")


    def step(self, actions):
        obs, privileged_obs, rew, reset, extras = super().step(actions)
        self.debug_print_joint_angles() 
        return obs, privileged_obs, rew, reset, extras