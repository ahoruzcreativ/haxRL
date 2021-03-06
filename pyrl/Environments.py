from Box import Box
from Vector import Vector, UnitVec
from Goal import Goal
from Disc import Disc
from Ball import Ball
from Scene import Scene
from Color import Color
from Way import Way
from VerticalBorder import VerticalBorder
from HorizontalBorder import HorizontalBorder
import random
from StateSequence import StateSequence
from StateProcessor import StateProcessor
from Player import Player
from Action import Action
from Side import Side
import numpy as np
from scipy.misc import imresize
from ActionSpace import ActionSpace
from config import c_width, c_height, middle_field_radius, topbottom_margin, \
leftright_margin, border_restitution, goal_length, ball_radius, ball_mass, \
ball_restitution, ball_damping, player_radius, player_mass, player_restitution, \
player_damping, player_kick_damping, player_kick_power



        
        

        
        
class HaxballEnvironment :
    def __init__(self, random_start = True, step_limit = None, ball_idle_limit = None, state_output_mode = 'pixels', rendering = True, frame_skip=4):
        self.action_space = ActionSpace([Action.up, Action.down, Action.forward, Action.backward, Action.nomoveshoot, Action.nomove])
        self.step_limit = step_limit
        self.ball_idle_limit = ball_idle_limit
        self.state_output_mode = state_output_mode
        self.rendering = rendering
        self.ball_idle = 0
        self.step_limit = step_limit
        if state_output_mode == 'pixels': self.rendering = True
        self.step_count = 0
        self.random_start = random_start
        self.frame_skip = frame_skip
    
    
        self.scene =  Scene(c_width, c_height)
        self.scene.add_object(Box(5, c_width - 5, 5, c_height - 5, 0))
        self.scene.add_object(Disc(c_width / 2, c_height / 2, middle_field_radius, 10, 1, 1, Color.white).make_ghost().make_hollow().set_outer_color(Color.border))
        self.scene.add_object(VerticalBorder(c_width / 2, c_height / 2, c_height - 2 * topbottom_margin, None).make_ghost())


        self.scene.add_object(HorizontalBorder(c_width / 2, topbottom_margin, c_width - 2 * leftright_margin, border_restitution).extend_to(Way.up).set_collision_mask([Ball]))
        self.scene.add_object(HorizontalBorder(c_width / 2, c_height - topbottom_margin, c_width - 2 * leftright_margin, border_restitution).extend_to(Way.down).set_collision_mask([Ball]))
        self.scene.add_object(VerticalBorder(leftright_margin, (c_height / 2 - goal_length / 2 + topbottom_margin) / 2, c_height / 2 - topbottom_margin - goal_length / 2, border_restitution).extend_to(Way.left).set_collision_mask([Ball]))
        self.scene.add_object(VerticalBorder(leftright_margin, c_height - (c_height / 2 - goal_length / 2 + topbottom_margin) / 2, c_height / 2 - topbottom_margin - goal_length / 2, border_restitution).extend_to(Way.left).set_collision_mask([Ball]))
        self.scene.add_object(VerticalBorder(c_width - leftright_margin, (c_height / 2 - goal_length / 2 + topbottom_margin) / 2, c_height / 2 - topbottom_margin - goal_length / 2, border_restitution).extend_to(Way.right).set_collision_mask([Ball]))
        self.scene.add_object(VerticalBorder(c_width - leftright_margin, c_height - (c_height / 2 - goal_length / 2 + topbottom_margin) / 2, c_height / 2 - topbottom_margin - goal_length / 2, border_restitution).extend_to(Way.right).set_collision_mask([Ball]))
        
       
        self.goal1 = Goal(leftright_margin, c_height / 2, Way.left, goal_length)
        self.goal2 = Goal(c_width - leftright_margin, c_height / 2, Way.right, goal_length)
        
        self.player1 = Player(120, c_height / 2, player_radius, player_mass, \
                                     player_restitution, player_damping, player_kick_damping, player_kick_power, Side.red)
       
        self.player2 = Player(c_width - 120, c_height / 2, player_radius, player_mass, \
                                     player_restitution, player_damping, player_kick_damping, player_kick_power, Side.blue)
       
        self.ball = Ball(c_width / 2, c_height / 2, ball_radius, ball_mass, ball_restitution, ball_damping)
        
        self.scene.add_object(self.goal1)
        self.scene.add_object(self.goal2)
        self.scene.add_object(self.player1)
        self.scene.add_object(self.player2)
        self.scene.add_object(self.ball)
        
        
        self.sequence1 = StateSequence([84, 84, 4])
        self.sequence2 = StateSequence([84, 84, 4])
        
        
    def step(self, action_red, action_blue = -1):
        #ai action no frameskip
        if self.player2.center.x > self.ball.center.x:
            if random.random() < 0.02:
                self.player2.apply_action(Action.nomoveshoot)
            else:
                self.player2.apply_action(Action.nomove)
                
        #agent action
        for n in range(self.frame_skip):
            self.player2.apply_force(self.ai_select_force())
            self.player1.apply_action(self.action_space[action_red])
            self.scene.update()
            self.step_count += 1

        if self.rendering == True:
            self.render()
            
        if self.ball.velocity.magnitude() < 0.1:
            self.ball_idle += 1
        else:
            self.ball_idle = 0

        
        return self._get_state_reward_done_info()
    
    def ai_select_force(self):
        ai_agent_pos = self.player2.center
        ball_pos = self.ball.center
        goal_pos = self.goal1.center
        unit_goal_to_ball = Vector.sub(ball_pos, goal_pos).normalize()
        
        attract_point = ball_pos.add(unit_goal_to_ball.mult(self.ball.radius))
        repel_point = ball_pos.sub(unit_goal_to_ball.mult(self.ball.radius))
        
        attract_force = Vector.sub(attract_point, ai_agent_pos)
        repel_force   = Vector.sub(ai_agent_pos, repel_point).mult(0.2)
        unit_total_force = Vector.add(attract_force, repel_force).normalize()
        
        return unit_total_force
        
        
    
    def render(self):
        self.scene.draw()
        
    def reset(self):
        self.scene.reset()
        self.ball_idle = 0
        self.episode_end = False
        if (self.random_start) :
            self.scene.meta_objects['balls'][0].apply_impulse(Vector(random.random() - 0.5, random.random() - 0.5).mult(20))
        self.step_count = 0
        self.render()
        
        return self._calculate_state()

    def _get_state_reward_done_info(self):
        state = self._calculate_state()
        reward = self._calculate_reward()
        
        done = self._calculate_done()
        
        info = self._calculate_info()
        
        return [state, reward, done, info]
    
    
    def _calculate_reward(self):
        v_player = self.player1.velocity
        v_ball   = self.ball.velocity
        
        player_to_ball_vec = Vector.sub(self.ball.center, self.player1.center)
        
        if Vector.dot(Vector.sub(v_player, v_ball), player_to_ball_vec) > 0:
            player_to_ball = 1
        else:
            player_to_ball = 0
            
        ball_to_goal_vec = Vector.sub(self.goal2.center, self.ball.center)
            
        if Vector.dot(v_ball, ball_to_goal_vec) > 0:
            ball_to_goal = 1
        else:
            ball_to_goal = 0
            
        goal = self._calculate_info()['goal']
        reward = goal
        
        return reward
    
    def _calculate_done(self):
        if self.step_limit == None or self.step_count < self.step_limit :
            step_limit_reached = False
        else:
            step_limit_reached = True
        
        if self.ball_idle_limit == None or self.ball_idle < self.ball_idle_limit:
            ball_idle_limit_reached = False
        else:
            ball_idle_limit_reached = True
        
        
        return self.scene.check_goals() or step_limit_reached or ball_idle_limit_reached 
        
    def _calculate_state(self):
        if self.state_output_mode == 'locations':    
            p1x = self.player1.center.x
            p1y = self.player1.center.y
            bx = self.ball.center.x
            by = self.ball.center.y
            p2x = self.player2.center.x
            p2y = self.player2.center.y
            
            horiz = c_width / 2
            vert = c_height / 2
            
            p1x = (p1x - horiz) / horiz
            p1y = (p1y - vert) / vert
            p2x = (p2x - horiz) / horiz
            p2y = (p2y - vert) / vert
            bx = (bx - horiz) / horiz
            by = (by - vert) / vert
            
            state_for_p1 = np.array([p1x, p1y, p2x, p2y, bx, by])
            state_for_p2 = np.array([-p2x, p2y, -p1x, p1y, -bx, by])
            return [state_for_p1, state_for_p2]
        
        
        elif self.state_output_mode == 'pixels':    
            obs_size = (400, 600) 
            pad_size = obs_size[0] // 2, obs_size[1] // 2
            obs = self.scene.get_scene_as_array()
            
#            obs = np.pad(obs[:,:,1], ((pad_size[0],), (pad_size[1],)) , 'edge')
            
            p1x = int(self.player1.center.x + pad_size[1]) 
            p1y = int(self.player1.center.y + pad_size[0])
#            p2x = int(self.player2.center.x + pad_size[1]) 
#            p2y = int(self.player2.center.y + pad_size[0])
#            obs1 = obs[p1y - obs_size[0] // 2: p1y + obs_size[0] // 2, p1x - obs_size[1] // 2: p1x + obs_size[1] // 2]
#            obs2 = obs[p2y - obs_size[0] // 2: p2y + obs_size[0] // 2, p2x - obs_size[1] // 2: p2x + obs_size[1] // 2]
            obs1 = obs[:,:,0]
            obs1 = imresize(obs1, (84, 84))
#            obs2 = imresize(obs2, (84, 84))
            self.sequence1.append_obs(obs1)
#            self.sequence2.append_obs(obs2[:,::-1])
            return self.sequence1.get_sequence()#, self.sequence1.get_sequence()
        else:
            raise Exception('invalid state output mode: {}'.format(self.state_output_mode))
        
        
    
    def _calculate_info(self):
        info = {
            "goal": 0,
            "ball_at_side": 0,
            "closer_player_to_ball": -1
        }
        
        
        if self.ball.center.x > c_width / 2:
            info['ball_at_side'] = 1
        elif self.ball.center.x < c_width / 2:
            info['ball_at_side'] = -1
        else:
            info['ball_at_side'] = 0
        
        if self.scene.check_goals():
            if info['ball_at_side'] == 1:
                info['goal'] = 1
            elif info['ball_at_side'] == -1:
                info['goal'] = -1
        
        if Vector.dist(self.player1.center, self.ball.center) < Vector.dist(self.player2.center, self.ball.center):
            info["closer_player_to_ball"] = 0
        else:
            info["closer_player_to_ball"] = 1
        return info
        
        
    def close(self):
        pass


#####################################
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
class PenaltyEnvironment:
    def __init__(self, frame_skip = 2):
        
        height = 400
        width = 600
        goal_length = 300
        self.scene =  Scene(width, height)
        self.frame_skip = frame_skip
        self.ball_idle = 0
        self.ball_idle_limit = 3

        self.action_space = ActionSpace([Action.up, Action.down, Action.nomoveshoot])
       
        self.box = Box(0, width, 0, height, 0)
        self.goal1 = Goal(leftright_margin, height / 2, Way.left, goal_length)

        self.player1 = Player(80, height / 2, player_radius, player_mass, \
                                     player_restitution, player_damping, player_kick_damping, player_kick_power, Side.red)
       
       
        self.ball = Ball(width - 100, height / 2, ball_radius, ball_mass, ball_restitution, ball_damping)
        self.penalty_spot = Disc(self.ball.center.x, self.ball.center.y, 4, 0, 0, 0, Color.green).make_ghost().make_hollow()
#        self.player_border_left = VerticalBorder(50, height / 2, height, 0, visible=True)
#        self.player_border_right = VerticalBorder(100, height / 2, height, 0, visible=True)
        
        self.scene.add_object(self.goal1)
        self.scene.add_object(self.player1)
        self.scene.add_object(self.ball)
        self.scene.add_object(self.penalty_spot)
        self.scene.add_object(self.box)
        self.reset()

#        self.scene.add_object(self.player_border_left)
#        self.scene.add_object(self.player_border_right)

    def step(self, action=1):
        for n in range(self.frame_skip):
            self.player1.apply_action(self.action_space[action])
            self.scene.update()
        
        if self.ball.velocity.magnitude() < 0.5:
            self.ball_idle += 1
            
        return self._get_state_reward_done_info()

    def reset(self):
        self.scene.reset()
        self.ball.apply_impulse(Vector(-25, random.random() * 16 - 8))
        self.ball_idle = 0
        
        
    def render(self):
        self.scene.draw()
        
    
    def _get_state_reward_done_info(self):
        state = self._calculate_state()
        reward = self._calculate_reward()
        
        done = self._calculate_done()
        
        info = self._calculate_info()
        
        return [state, reward, done, info]
    
    
    def _calculate_state(self):
        self.scene.draw()
        obs = self.scene.get_scene_as_array()
        return imresize(obs, [210,160])
        
    
    def _calculate_reward(self):
        if self.scene.check_goals():
            return -1
        elif self.ball_idle > self.ball_idle_limit:
            return 1
        else:
            return 0
    
        
    def _calculate_done(self):
            return self.scene.check_goals() or self.ball_idle > self.ball_idle_limit
        
    
    def _calculate_info(self):
        return {}