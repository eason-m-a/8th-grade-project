import arcade, math, entity_classes, random

ROPE_SCALE = 1

class Launcher(arcade.Sprite):
    def setup(self, anchor_sprite, projectile_list, button_type, launch_power, bounce_mult, proj_gravity, air_resist, damage):
        self.anchor_sprite = anchor_sprite
        self.angle = 90
        self.projectile_list = projectile_list
        self.button_type = button_type
        self.launch_power = launch_power
        self.bounce_mult = bounce_mult
        self.proj_gravity = proj_gravity
        self.air_resist = air_resist
        self.damage = damage
        self.strength = self.anchor_sprite.strength
        self.alpha = 0

    def update(self):
        self.strength = self.anchor_sprite.strength
        self.set_position(self.anchor_sprite.center_x, self.anchor_sprite.top)
        if any(map(lambda projectile: projectile.thrown, self.projectile_list)):
            self.alpha = 255
        else:
            self.alpha = 0

    def adjust_angle(self, shot_projectile_sprite):
        self.angle = shot_projectile_sprite.angle


class Projectile(arcade.Sprite):
    def setup(self, launcher, window, id, boundary_type):
        self.launcher = launcher
        self.window = window
        self.id = id
        self.boundary_type = boundary_type
        self.set_position(self.launcher.center_x, self.launcher.center_y)
        self.thrown = False
        self.retracting = False
        self.grounded = False
        self.ground_frame = None
        self.speed = 0
        self.alpha = 0
        self.x_vector = 0
        self.y_vector = 0
        self.set_position(self.launcher.center_x, self.launcher.center_y)

    def update(self):
        self.check_if_offscreen()
        if self.retracting:
            self.when_retracting()
        if not self.grounded:
            self.x_vector *= self.launcher.air_resist
            self.y_vector -= self.launcher.proj_gravity
            self.set_position(self.center_x + self.x_vector, self.center_y + self.y_vector)
            self.radians = math.atan2(self.y_vector, self.x_vector)

    def check_if_offscreen(self):
        if self.thrown and not self.retracting:
            if (self.top <= 0 or self.bottom >= self.window.height or self.right <= 0 or self.left >= self.window.width) and self.boundary_type == 1:
                self.retracting = True
            if (self.center_y <= 0 or self.center_y >= self.window.height or self.center_x <= 0 or self.center_x >= self.window.width) and self.boundary_type == 2:
                self.retracting = True
            if (self.bottom <= 0 or self.top >= self.window.height or self.left <= 0 or self.right >= self.window.width) and self.boundary_type == 3:
                self.retracting = True

            if self.retracting:
                self.on_retract()

    def throw(self, target_x, target_y):
        if not self.thrown:
            self.set_position(self.launcher.center_x, self.launcher.center_y)
            self.thrown = True
            self.radians = math.atan2((target_y - self.center_y), (target_x - self.center_x))
            self.speed = self.launcher.launch_power
            self.x_vector = -self.speed * math.sin(self.radians - math.pi/2)
            self.y_vector = self.speed * math.cos(self.radians - math.pi/2)
            self.alpha = 255

    def when_retracting(self):
        pass

    def on_retract(self):
        pass


class DamagingProjectile(Projectile, entity_classes.AttackerSprite):
    def setup(self, launcher, window, id, boundary_type, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength):
        self.body_sprite = self
        Projectile.setup(self, launcher, window, id, boundary_type)
        entity_classes.AttackerSprite.setup(self, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.gravity = 0
        self.friction = 1

    def update(self):
        self.damage = self.launcher.damage
        self.strength = self.launcher.strength
        Projectile.update(self)
        entity_classes.AttackerSprite.update(self)


class Rope(arcade.Sprite):
    def setup(self, launcher, attached_projectile_list, id):
        self.launcher = launcher
        self.attached_projectile_list = attached_projectile_list
        self.id = id
        self.width = 0

        self.textures = [arcade.load_texture("rope.png")]
        self.set_texture(0)
        self.scale = ROPE_SCALE

    def update(self):
        if self.attached_projectile_list[self.id].thrown:
            self.center_x = (self.attached_projectile_list[self.id].center_x + self.launcher.center_x)/2
            self.center_y = (self.attached_projectile_list[self.id].center_y + self.launcher.center_y)/2
            self.radians = math.atan2((self.attached_projectile_list[self.id].center_y - self.center_y), (self.attached_projectile_list[self.id].center_x - self.center_x))
            self.width = ((self.attached_projectile_list[self.id].center_x - self.launcher.center_x)**2 + (self.attached_projectile_list[self.id].center_y - self.launcher.center_y)**2)**0.5
        else:
            self.width = 0


class Explosion(entity_classes.AttackerSprite):
    def setup(self, window, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength, duration):
        super().setup(target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.gravity = 0
        self.friction = 1
        self.body_sprite = self
        self.window = window
        self.duration = duration
        self.creation_frame = window.frame
        self.original_x = self.center_x
        self.original_y = self.center_y

    def update(self):
        if self.creation_frame == self.window.frame:
            super().update()
        if self.creation_frame + self.duration <= self.window.frame:
            self.kill()
        intensity = 5
        self.set_position(self.original_x + random.randint(-intensity, intensity), self.original_y + random.randint(-intensity, intensity))