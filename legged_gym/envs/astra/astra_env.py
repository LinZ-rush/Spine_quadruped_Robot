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