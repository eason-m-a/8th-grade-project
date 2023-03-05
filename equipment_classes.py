import arcade, projectile_classes, entity_classes, enemy_classes, math

GRAPPLE_SCALE = 1
HELMET_SCALE = 1
CRAB_SCALE = 1
SWORD_SCALE = 1
ARROW_SCALE = 1
ARROW_PICKUP_DELAY = 10
ARROW_LIFE_SPAN = 400

class Grapple(projectile_classes.Projectile):
    def setup(self, launcher, window, id, boundary_type):
        super().setup(launcher, window, id, boundary_type)
        self.textures = [arcade.load_texture("grapple.png")]
        self.set_texture(0)
        self.scale = GRAPPLE_SCALE

    def update(self):
        super().update()
        if self.thrown:
            grappling_hook_hit_list = list(filter(lambda coin: coin.puller_id == None, arcade.check_for_collision_with_list(self, self.window.coin_list)))
            for coin in grappling_hook_hit_list:
                coin.pulled = True
                coin.puller_id = self.id

            if len(grappling_hook_hit_list) > 0 and not self.retracting:
                self.retracting = True

    def when_retracting(self):
        self.radians = math.atan2((self.launcher.center_y - self.center_y), (self.launcher.center_x - self.center_x))
        self.x_vector = self.speed * math.cos(self.radians)
        self.y_vector = self.speed * math.sin(self.radians)
        if arcade.check_for_collision(self, self.launcher):
            self.setup(self.launcher, self.window, self.id, self.boundary_type)

    def on_retract(self):
        self.radians = math.atan2((self.launcher.center_y - self.center_y), (self.launcher.center_x - self.center_x))


class Arrow(projectile_classes.DamagingProjectile):
    def setup(self, launcher, window, id, boundary_type, target_list, frame_delay, kb_x, kb_y, gravity, friction, strength):
        damage = launcher.damage
        super().setup(launcher, window, id, boundary_type, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.bounce_num = 0
        self.max_bounce_num = 0
        self.textures = [arcade.load_texture("arrow.png")]
        self.set_texture(0)
        self.scale = ARROW_SCALE

    def when_retracting(self):
        if not self.grounded:
            self.bounce()
        if self.grounded:
            self.alpha -= 255/ARROW_LIFE_SPAN
            if self.ground_frame + ARROW_LIFE_SPAN == self.window.frame:
                self.top = -2000
            elif (arcade.check_for_collision_with_list(self, self.window.player_list) and self.window.frame > self.ground_frame + ARROW_PICKUP_DELAY) or self.ground_frame + ARROW_LIFE_SPAN < self.window.frame:
                self.setup(self.launcher, self.window, self.id, self.boundary_type, self.target_list, self.frame_delay, self.kb_x, self.kb_y, self.gravity, self.friction, self.strength)

    def on_retract(self):
        self.bounce()

    def bounce(self):
        if self.center_x < 0 or self.center_x > self.window.width or self.center_y < self.window.player_sprite_torso.ground_y or self.center_y > self.window.height:
            self.bounce_num += 1
            if self.center_x < 0 or self.center_x > self.window.width:
                self.x_vector *= -self.launcher.bounce_mult
                if self.center_x < 0:
                    self.center_x = 0
                if self.center_x > self.window.width:
                    self.center_x = self.window.width
            if self.center_y < self.window.player_sprite_torso.ground_y or self.center_y > self.window.height:
                self.y_vector *= -self.launcher.bounce_mult
                if self.center_y < self.window.player_sprite_torso.ground_y:
                    self.center_y = self.window.player_sprite_torso.ground_y
                    if self.bounce_num > self.max_bounce_num:
                        self.grounded = True
                        self.ground_frame = self.window.frame
                if self.center_y > self.window.height:
                    self.center_y = self.window.height

    def attack(self, target_sprite):
        if not self.grounded:
            projectile_classes.DamagingProjectile.attack(self, target_sprite)


class Weapon(entity_classes.AttackerSprite):
    def setup(self, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength, window, owner):
        super().setup(target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.window = window
        self.owner = owner
        self.body_sprite = self
        self.set_position(self.owner.center_x, self.owner.center_y)

    def update(self):
        super().update()
        self.damage = self.owner.damage
        self.strength = self.owner.strength


class Sword(Weapon):
    def setup(self, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength, window, owner):
        super().setup(target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength, window, owner)
        self.textures = [arcade.load_texture("sword.png")]
        self.set_texture(0)
        self.scale = SWORD_SCALE

    def update(self):
        super().update()
        dist_from_player = 100
        self.angle = self.window.frame % 360
        self.set_position(self.window.player_sprite_torso.center_x + -dist_from_player * math.sin(self.radians), self.window.player_sprite_torso.center_y + dist_from_player * math.cos(self.radians))
        self.angle += 90


class Clothes(arcade.Sprite):
    def setup(self, body_part, x_just, y_just, window):
        self.body_part = body_part
        self.x_just = x_just
        self.y_just = y_just
        self.window = window
        self.set_position(self.body_part.center_x + self.x_just, self.body_part.center_y + self.y_just)
        self.angle = self.body_part.angle

    def update(self):
        self.set_position(self.body_part.center_x + self.x_just, self.body_part.center_y + self.y_just)
        self.angle = self.body_part.angle
        self.scale = self.body_part.scale

class Hat(Clothes):
    def setup(self, body_part, x_just, y_just, window):
        super().setup(body_part, x_just, y_just, window)
        self.textures = [arcade.load_texture("helmet.png", mirrored=True), arcade.load_texture("helmet.png")]
        self.set_texture(1)
        if self.window.player_sprite_torso.direction == -1:
            self.set_texture(0)
        elif self.window.player_sprite_torso.direction == 1:
            self.set_texture(1)

    def update(self):
        if self.window.player_sprite_torso.direction == -1:
            self.set_texture(0)
        elif self.window.player_sprite_torso.direction == 1:
            self.set_texture(1)
        super().update()


class Shoe(Clothes):
    def setup(self, body_part, x_just, y_just, window):
        super().setup(body_part, x_just, y_just, window)
        self.textures = [arcade.load_texture("shoe.png"), arcade.load_texture("shoe.png", flipped=True)]
        self.set_texture(0)

    def update(self):
        super().update()
        self.set_texture(self.body_part.texture_index - 1)

class Crab(enemy_classes.WalkingEnemy):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.grab_distance = 125
        self.textures = [arcade.load_texture("grab crab.png", mirrored=True), arcade.load_texture("grab crab.png")]
        self.set_texture(1)
        self.scale = CRAB_SCALE
        self.set_position(-self.width, 0)

    def update(self):
        super().update()
        for coin in self.window.coin_list:
            if arcade.get_distance_between_sprites(self, coin) < self.grab_distance:
                coin.die()