import arcade, math, entity_classes

PLAYER_SCALE = 1

class Limb(entity_classes.DamagableSprite):
    def setup(self, body_sprite, window, modifier, id, height_mod, type, hp, defense):
        self.textures = [arcade.load_texture("stick man limb half.png"), arcade.load_texture("stick man bottom leg half.png"), arcade.load_texture("stick man bottom leg half.png", flipped=True), arcade.load_texture("stick man top arm half.png")]
        self.set_texture(0)
        self.base_scale = PLAYER_SCALE
        self.scale = self.base_scale

        super().setup(body_sprite, window, hp, defense)
        self.start_pos = ()
        self.end_pos = ()
        self.joint_point = ()
        self.modifier = modifier
        self.id = id
        self.height_mod = height_mod
        self.type_is_arm = type
        self.walk_frames = 60
        self.idle_frames = 60/2
        self.set_anim_vars(-999)
        self.texture_index = 0

        self.outline = arcade.Sprite()
        self.outline.textures = [arcade.load_texture("stick man limb half outline.png"), arcade.load_texture("stick man bottom leg half outline.png"), arcade.load_texture("stick man bottom leg half outline.png", flipped=True), arcade.load_texture("stick man top arm half outline.png")]
        self.outline.set_texture(0)
        self.window.player_limb_outline_list.append(self.outline)

        if self.id == 1 and self.type_is_arm:
            self.texture_index = 3
            self.set_texture(self.texture_index)
            self.outline.set_texture(self.texture_index)
        self.scale = PLAYER_SCALE
        self.outline.scale = PLAYER_SCALE

    def update(self):
        super().update()
        self.set_poses()
        hypot = math.sqrt((self.start_pos[0] - self.end_pos[0]) ** 2 + (self.start_pos[1] - self.end_pos[1]) ** 2)
        leg = self.width
        if "walking" in self.player_state:
            if "left" in self.player_state:
                direction = -1
            else:
                direction = 1
            if self.type_is_arm:
                direction *= -1

            height = math.sqrt(leg ** 2 - (hypot/2) ** 2) * direction
        else:
            height = math.sqrt(leg ** 2 - (hypot/2) ** 2) * self.height_mod
        inner_angle = math.atan2(height, hypot/2)
        outer_angle = math.atan2(self.end_pos[1] - self.start_pos[1], self.end_pos[0] - self.start_pos[0])
        self.joint_point = (math.cos(inner_angle + outer_angle) * leg + self.start_pos[0], math.sin(inner_angle + outer_angle) * leg + self.start_pos[1])
        self.angle = (inner_angle + outer_angle) * 180/math.pi

        if self.id == 0:
            self.set_position((self.start_pos[0] + self.joint_point[0])/2, (self.start_pos[1] + self.joint_point[1])/2)
        else:
            self.angle += 180 - inner_angle * 2 * 180/math.pi
            self.set_position((self.end_pos[0] + self.joint_point[0])/2, (self.end_pos[1] + self.joint_point[1])/2)

        self.outline.scale = self.scale
        self.outline.angle = self.angle
        self.outline.set_position(self.center_x, self.center_y)

    def set_poses(self):
        if self.type_is_arm:
            arm_start_pos = (30, 30)
            self.start_pos = (self.body_sprite.center_x + self.body_sprite.width/2 * self.modifier, self.body_sprite.center_y)
            self.end_pos = (self.start_pos[0] + arm_start_pos[0] * self.modifier, self.start_pos[1] + arm_start_pos[1])
        else:
            leg_start_pos = (10, -40)
            self.start_pos = (self.body_sprite.center_x + self.body_sprite.width/2 * math.sqrt(2)/2 * self.modifier, self.body_sprite.center_y - self.body_sprite.width/2 * math.sqrt(2)/2)
            self.end_pos = (self.start_pos[0] + leg_start_pos[0] * self.modifier, self.start_pos[1] + leg_start_pos[1])

        end_x = self.end_pos[0]
        end_y = self.end_pos[1]

        if self.player_state == "idle":
            if self.type_is_arm:
                if self.body_sprite.jumping[0]:
                    end_x = self.end_pos[0] - (math.cos((-self.body_sprite.y_vector + self.body_sprite.jump_speed)/self.body_sprite.jump_speed * math.pi) * self.body_sprite.idle_intensity) * -self.modifier * self.body_sprite.jump_intensity/2
                    end_y = self.end_pos[1] - math.cos((-self.body_sprite.y_vector + self.body_sprite.jump_speed)/self.body_sprite.jump_speed * math.pi) * self.body_sprite.idle_intensity * self.body_sprite.jump_intensity
                else:
                    end_x = self.end_pos[0] - (math.cos((self.window.frame - self.ani_start_frame)/(self.idle_frames) * math.pi) * self.body_sprite.idle_intensity) * 0.5 * -self.modifier
                    end_y = self.end_pos[1] - math.cos((self.window.frame - self.ani_start_frame)/(self.idle_frames) * math.pi) * self.body_sprite.idle_intensity
            else:
                if self.body_sprite.jumping[0]:
                    end_y = self.end_pos[1] - math.cos((-self.body_sprite.y_vector + self.body_sprite.jump_speed)/self.body_sprite.jump_speed * math.pi) * self.body_sprite.idle_intensity * self.body_sprite.jump_intensity
                else:
                    end_y = self.body_sprite.ground_y
                if self.id == 1:
                    self.texture_index = int((self.modifier + 1)/2 + 1)
                    self.set_texture(self.texture_index)
                    self.outline.set_texture(self.texture_index)
        elif "walking" in self.player_state:
            if "left" in self.player_state:
                direction = -1
            else:
                direction = 1
            frame_dif = self.window.frame - self.ani_start_frame
            if self.type_is_arm:
                circle_rad = 15
                revolve_dist = 5
                end_x = self.body_sprite.center_x + self.body_sprite.width/2 * direction + revolve_dist * direction + circle_rad * math.cos(frame_dif * self.body_sprite.speed * 360/(self.walk_frames * 5) * math.pi/180) * -self.modifier
                end_y = self.end_pos[1] + -circle_rad * math.sin(frame_dif * self.body_sprite.speed * 360/(self.walk_frames * 5) * math.pi/180) * -self.modifier + circle_rad
            else:
                circle_rad = 15
                end_x = self.end_pos[0] + circle_rad * math.cos(frame_dif * self.body_sprite.speed * 360/(self.walk_frames * 5) * math.pi/180) * -self.modifier
                if self.modifier != direction:
                    end_y = self.end_pos[1] + -circle_rad * math.sin(frame_dif * self.body_sprite.speed * 360/(self.walk_frames * 5) * math.pi/180) + circle_rad
                else:
                    end_y = self.end_pos[1] + circle_rad * math.sin(frame_dif * self.body_sprite.speed * 360/(self.walk_frames * 5) * math.pi/180) + circle_rad
                if self.id == 1:
                    self.texture_index = int((direction + 1)/2 + 1)
                    self.set_texture(self.texture_index)
                    self.outline.set_texture(self.texture_index)
        elif self.player_state == "launching":
            pass
            if all(map(lambda projectile_list: all(map(lambda projectile: not projectile.thrown, projectile_list)), map(lambda launcher: launcher.projectile_list, self.window.launcher_list))) and 0:
                self.player_state = self.body_sprite.states[0]
            end_x = self.body_sprite.center_x + 20 * self.modifier
            end_y = self.body_sprite.top - 5

        self.end_pos = (end_x, end_y)
        self.scale = self.base_scale

    def set_anim_vars(self, start_frame):
        self.player_state = self.body_sprite.states[self.type_is_arm]
        self.ani_start_frame = start_frame


class Head(entity_classes.DamagableSprite):
    def setup(self, body_sprite, window, hp, defense):
        self.textures = [arcade.load_texture("stick man head.png", mirrored=True), arcade.load_texture("stick man head.png"), arcade.load_texture("stick man head dead.png")]
        self.set_texture(1)
        self.base_scale = PLAYER_SCALE
        self.scale = self.base_scale


        super().setup(body_sprite, window, hp, defense)
        self.center_x = self.body_sprite.center_x
        self.bottom = self.body_sprite.top
        self.id = None

    def update(self):
        super().update()
        self.center_x = self.body_sprite.center_x
        self.scale = self.base_scale


class Torso(entity_classes.DamagableSprite):
    def setup(self, body_sprite, window, hp, defense):
        self.textures = [arcade.load_texture("stick man torso.png")]
        self.set_texture(0)
        self.base_scale = PLAYER_SCALE
        self.scale = self.base_scale

        super().setup(body_sprite, window, hp, defense)

        self.base_y = self.height/2 + 100
        self.ground_y = math.floor(self.base_y - self.width/2 * math.sqrt(2)/2 - 40)
        self.set_position(window.width/2, self.base_y)
        self.direction = 0
        self.previous_player_direction = 0
        self.x_vector = 0
        self.y_vector = 0
        self.base_speed = 5
        self.speed = self.base_speed
        self.base_jump_speed = 10
        self.jump_speed = self.base_jump_speed
        self.jumping = [False, False]
        self.gravity = 0.5
        self.states = ["idle", "idle"]
        self.angle = 0
        self.id = None
        self.idle_intensity = 10
        self.jump_intensity = 2

        self.frame_delay = 20
        self.damage = 50
        self.strength = 1

    def update(self):
        super().update()
        if self.top > self.window.height:
            self.top = self.window.height
            self.y_vector = abs(self.y_vector) * -0.5

        self.x_vector *= 0.95
        if abs(self.x_vector) < 1:
            self.x_vector = 0

        #set player state to launching if any projectile is thrown
        if any(map(lambda launcher: any(map(lambda projectile: projectile.thrown, launcher.projectile_list)), self.window.launcher_list)):
            self.states[1] = "launching"

        #if no projectiles are thrown and the player is launching, arms no longer are launching and update limbs
        if all(map(lambda launcher: all(map(lambda projectile: not projectile.thrown, launcher.projectile_list)), self.window.launcher_list)) and self.states[1] != self.states[0]:
            self.states[1] = self.states[0]
            self.window.update_limb_vars()

        #set player to jumping if player has y vector (not on ground)
        if self.y_vector != 0:
            self.jumping[0] = True

        if self.hp > self.max_hp:
            self.hp = self.max_hp

        self.scale = self.base_scale

    def on_hurt(self, attacker):
        super().on_hurt(attacker)
        if self.hp <= 0:
            self.window.lost = True