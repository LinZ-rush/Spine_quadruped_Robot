# legged_gym/envs/astra/astra_env.py

from legged_gym.envs.base.legged_robot import LeggedRobot
from isaacgym import gymtorch, gymapi
import torch
from .astra_config import AstraFlatCfg

class AstraRobot(LeggedRobot):
    cfg: AstraFlatCfg

    def _init_buffers(self):
        # ==========================================================
        # 1. 【核心修复】 防止父类初始化时 crash
        # ==========================================================
        # 备份真实的动作维度 (12)
        original_num_actions = self.num_actions
        
        # 临时将 num_actions 设为 num_dof (15)
        # 这样父类在初始化 p_gains/d_gains/torques 时就会创建 15 维的数组
        # 从而在遍历 15 个关节赋 PD 值时不会报 IndexError
        self.num_actions = self.num_dof
        
        # 安全调用父类初始化
        super()._init_buffers()
        
        # ==========================================================
        # 2. 【还原设置】 将维度改回 12 以适配 RL 策略
        # ==========================================================
        self.num_actions = original_num_actions
        
        # 重新初始化 actions 和 last_actions 为 12 维
        # (因为刚才父类把它们初始化成了 15 维)
        self.actions = torch.zeros(self.num_envs, self.num_actions, dtype=torch.float, device=self.device, requires_grad=False)
        self.last_actions = torch.zeros(self.num_envs, self.num_actions, dtype=torch.float, device=self.device, requires_grad=False)
        
        # 注意：self.torques, self.p_gains, self.d_gains 此时保留为 15 维
        # 这正是我们想要的！(物理引擎需要 15 维力矩，计算过程也需要 15 维 PD)

        # ==========================================================
        # 3. 识别关节索引
        # ==========================================================
        self.spine_keywords = ["spine", "DU", "Base"]
        self.spine_dof_indices = torch.tensor([i for i, name in enumerate(self.dof_names) if any(k in name for k in self.spine_keywords)], device=self.device, dtype=torch.long)
        self.leg_dof_indices = torch.tensor([i for i in range(self.num_dofs) if i not in self.spine_dof_indices.tolist()], device=self.device, dtype=torch.long)
        
        print(f"[AstraEnv] Buffer Init Success. Legs: {len(self.leg_dof_indices)}, Spine: {len(self.spine_dof_indices)}")

    def _pre_physics_step(self, actions):
        self.actions = actions.clone()
        
        # 1. 扩展 actions (12) -> (15)
        actions_scaled = actions * self.cfg.control.action_scale
        expanded_actions = torch.zeros(self.num_envs, self.num_dof, device=self.device)
        expanded_actions[:, self.leg_dof_indices] = actions_scaled
        
        # 2. 计算目标位置 (脊柱部分为 0，即保持默认)
        targets = self.default_dof_pos + expanded_actions
        
        # 3. 强制锁定脊柱目标
        targets[:, self.spine_dof_indices] = self.default_dof_pos[:, self.spine_dof_indices]

        # 发送目标
        self.gym.set_dof_position_target_tensor(self.sim, gymtorch.unwrap_tensor(targets))

    def _compute_torques(self, actions):
        # 1. 扩展 actions (12) -> (15)
        actions_scaled = actions * self.cfg.control.action_scale
        expanded_actions = torch.zeros(self.num_envs, self.num_dof, device=self.device)
        expanded_actions[:, self.leg_dof_indices] = actions_scaled
        
        # 2. 计算 15 维 PD 力矩
        control_type = self.cfg.control.control_type
        if control_type == "P":
            target_pos = self.default_dof_pos + expanded_actions
            torques = self.p_gains * (target_pos - self.dof_pos) - self.d_gains * self.dof_vel
        else:
            torques = torch.zeros_like(self.dof_pos)
            
        return torques

    def _get_noise_scale_vec(self, cfg):
        # 重写此函数以解决父类针对 12 DoF 硬编码索引的问题
        noise_vec = torch.zeros_like(self.obs_buf[0])
        self.add_noise = self.cfg.noise.add_noise
        noise_scales = self.cfg.noise.noise_scales
        noise_level = self.cfg.noise.noise_level
        
        # 基础状态噪声
        noise_vec[:3] = noise_scales.lin_vel * noise_level * self.obs_scales.lin_vel
        noise_vec[3:6] = noise_scales.ang_vel * noise_level * self.obs_scales.ang_vel
        noise_vec[6:9] = noise_scales.gravity * noise_level
        noise_vec[9:12] = 0. # commands
        
        # 动态计算关节索引范围 (适配 15 DoF)
        dof_pos_start = 12
        dof_pos_end = 12 + self.num_dof
        dof_vel_start = dof_pos_end
        dof_vel_end = dof_vel_start + self.num_dof
        
        noise_vec[dof_pos_start:dof_pos_end] = noise_scales.dof_pos * noise_level * self.obs_scales.dof_pos
        noise_vec[dof_vel_start:dof_vel_end] = noise_scales.dof_vel * noise_level * self.obs_scales.dof_vel
        
        # 上一次动作噪声
        action_start = dof_vel_end
        action_end = action_start + self.num_actions
        noise_vec[action_start:action_end] = 0. # previous actions
        
        if self.cfg.terrain.measure_heights:
            noise_vec[action_end:action_end+187] = noise_scales.height_measurements* noise_level * self.obs_scales.height_measurements
            
        return noise_vec