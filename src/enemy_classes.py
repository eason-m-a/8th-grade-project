import arcade, random, entity_classes, projectile_classes, equipment_classes, math

ENEMY_SCALE = 1
ENEMY_PROJECTILE_SCALE = 1
GOMBA_GRAVITY = 0.25
GOMBA_FRICTION = 0.9
GOMBA_BOUNCE_INTENSITY = 10
GOMBA_KNOCKBACK_X = 15
GOMBA_KNOCKBACK_Y = 15
ENEMY_DEAD_FRAMES = 45
TELEGRAPH_FRAMES = 60

class Enemy(entity_classes.DamagableAttacker):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.creation_frame = window.frame
        self.base_scale = ENEMY_SCALE
        self.scale = ENEMY_SCALE
        self.x_vector = 0
        self.y_vector = 0
        self.airborne = False
        self.in_game = False

        self.speed = speed
        self.worth = worth

        self.health_bar_texture = arcade.load_texture(r"assets\enemy health bar.png")
        self.health_bar_backing = arcade.Sprite(r"assets\red pixel.png", 1)
        self.health_bar_backing.alpha = 0
        self.health_bar_backing.height = self.health_bar_texture.height
        self.health_bar_backing.width = self.health_bar_texture.width
        self.window.enemy_health_bar_list.append(self.health_bar_backing)

        self.health_bar_filling = arcade.Sprite(r"assets\green pixel.png", 1)
        self.health_bar_filling.alpha = 0
        self.health_bar_filling.height = self.health_bar_texture.height
        self.window.enemy_health_bar_list.append(self.health_bar_filling)

        self.health_bar = arcade.Sprite(r"assets\enemy health bar.png", ENEMY_SCALE)
        self.health_bar.alpha = 0
        self.window.enemy_health_bar_list.append(self.health_bar)

    def update(self):
        super().update()
        if not self.is_dead:
            if self.bottom < self.window.player_sprite_torso.ground_y:
                self.bottom = self.window.player_sprite_torso.ground_y
                self.y_vector = 0
                if self.gravity != 0:
                    self.airborne = False
            elif self.bottom > self.window.player_sprite_torso.ground_y:
                if self.top > self.window.height:
                    self.top = self.window.height
                    self.y_vector *= -0.5
                self.y_vector -= self.gravity
                self.airborne = True
            if not (self.left < 0 or self.right > self.window.width) and not self.in_game:
                self.in_game = True
            if self.in_game:
                if self.left < 0:
                    self.left = 0
                elif self.right > self.window.width:
                    self.right = self.window.width
            self.x_vector *= self.friction
            if abs(self.x_vector) < 1:
                self.x_vector = 0
            self.health_bar.set_position(self.center_x, self.top + self.health_bar.height)
            self.health_bar_backing.set_position(self.center_x, self.top + self.health_bar.height)
            self.health_bar_filling.width = self.health_bar.width * self.hp/self.max_hp
            self.health_bar_filling.set_position(self.health_bar.center_x + (self.health_bar.width/2 * self.hp/self.max_hp) - self.health_bar.width/2 , self.health_bar.center_y)

    def attack_register(self, target_sprite):
        super().attack_register(target_sprite)

    def on_hurt(self, attacker):
        super().on_hurt(attacker)
        if self.bottom == self.window.player_sprite_torso.ground_y and self.y_vector < 0:
            self.y_vector = 0
        self.health_bar.alpha = 255
        self.health_bar_backing.alpha = 255
        self.health_bar_filling.alpha = 255
        if self.hp <= 0 and not self.is_dead:
            self.die()

    def die(self):
        self.is_dead = True
        self.health_bar.kill()
        self.health_bar_backing.kill()
        self.health_bar_filling.kill()
        self.x_vector = 0
        self.y_vector = 0
        self.window.money += self.worth
        self.die_frame = self.window.frame


class WalkingEnemy(Enemy):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.direction = 1

    def update(self):
        if not self.is_dead:
            self.set_position(self.center_x + self.x_vector + self.speed * self.direction, self.center_y + self.y_vector)
            if self.left < 0:
                self.direction = 1
                self.set_texture(1)
                self.scale = self.base_scale
            elif self.right > self.window.width:
                self.direction = -1
                self.set_texture(0)
                self.scale = self.base_scale
        super().update()


class Gomba(WalkingEnemy):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\gomba.png", mirrored=True), arcade.load_texture(r"assets\gomba.png")]
        self.set_texture(1)

    def update(self):
        if self.is_dead and self.die_frame + ENEMY_DEAD_FRAMES < self.window.frame:
            self.kill()
        super().update()

    def attack_register(self, target_sprite):
        if target_sprite.jumping[0] and not (any(map(lambda body_part: body_part.bottom < self.bottom, self.target_list)) and self.y_vector < 0):
            if not target_sprite in map(lambda tup: tup[0], self.invincibility_list):
                target_sprite.y_vector = GOMBA_BOUNCE_INTENSITY + self.y_vector * (self.y_vector > 0)
                self.hp -= target_sprite.damage
                self.on_hurt(target_sprite)
        else:
            self.hurt_player(target_sprite)

    def hurt_player(self, target_sprite):
        super().attack_register(target_sprite)

    def on_hurt(self, attacker):
        super().on_hurt(attacker)

    def die(self):
        super().die()
        self.center_y -= 7 / 16 * self.height
        self.width = self.width * 1.5
        self.height = self.height * 0.25


class Romba(Gomba):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)

        self.textures = [arcade.load_texture(r"assets\romba.png", mirrored=True), arcade.load_texture(r"assets\romba.png"), arcade.load_texture(r"assets\romba falling.png")]
        self.set_texture(1)

    def update(self):
        if not self.is_dead:
            if self.y_vector < 0:
                self.set_texture(2)
                self.scale = self.base_scale
            else:
                if self.direction == 1:
                    self.set_texture(1)
                    self.scale = self.base_scale
                elif self.direction == -1:
                    self.set_texture(0)
                    self.scale = self.base_scale
        super().update()

    def hurt_player(self, target_sprite):
        if self.y_vector < 0:
            self.damage *= 10
        super().hurt_player(target_sprite)
        if self.y_vector < 0:
            self.damage /= 10


class Bomba(Gomba):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\bomba.png", mirrored=True), arcade.load_texture(r"assets\bomba.png")]
        self.set_texture(1)
        self.shaking = False
        self.die_x = None
        self.die_y = None

    def update(self):
        if self.hp < self.max_hp:
            self.hp = 0
        WalkingEnemy.update(self)
        if self.is_dead and self.die_frame + ENEMY_DEAD_FRAMES * 2 < self.window.frame:
            self.explode()
        if self.shaking:
            shake_intensity = 5
            self.set_position(self.die_x + random.randint(-shake_intensity, shake_intensity), self.die_y + random.randint(-shake_intensity, shake_intensity))

    def attack_register(self, target_sprite):
        if (target_sprite.y_vector < 0 or all(map(lambda body_part: body_part.bottom >= self.center_y, self.target_list))) and not (any(map(lambda body_part: body_part.bottom < self.bottom, self.target_list)) and self.y_vector < 0):
            if not target_sprite in map(lambda tup: tup[0], self.invincibility_list):
                target_sprite.y_vector = GOMBA_BOUNCE_INTENSITY + self.y_vector * (self.y_vector > 0)
                self.hp = 0
                self.shaking = True
                self.on_hurt(target_sprite)
        else:
            self.hurt_player(target_sprite)

    def hurt_player(self, target_sprite):
        self.explode()

    def die(self):
        self.die_x = self.center_x
        self.die_y = self.center_y
        super().die()
        self.set_position(self.die_x, self.die_y)
        self.scale = self.base_scale
        if not self.shaking:
            self.explode()

    def explode(self):
        explosion = projectile_classes.Explosion()
        explosion.set_position(self.center_x, self.center_y)
        explosion.setup(self.window, self.target_list, self.damage, self.frame_delay, self.kb_x, self.kb_y, 0, 0, 1, ENEMY_DEAD_FRAMES)
        explosion.textures = [arcade.load_texture(r"assets\bomba explosion.png")]
        explosion.set_texture(0)
        explosion.scale = self.base_scale * 4
        self.window.enemy_projectile_list.append(explosion)
        self.kill()


class Jomba(Gomba):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)

        self.textures = [arcade.load_texture(r"assets\jomba.png", mirrored=True), arcade.load_texture(r"assets\jomba.png")]
        self.set_texture(1)

    def update(self):
        super().update()
        if not self.is_dead:
            if (self.window.frame + self.creation_frame + 1) % 300 == 0:
                self.jump_aura()

    def jump_aura(self):
        for enemy in self.window.enemy_list:
            if arcade.get_distance_between_sprites(self, enemy) < 200 and not enemy.airborne:
                enemy.y_vector += 15


class Vomba(Gomba):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength, launch_power, bounce_mult, proj_gravity, air_resist):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.launch_power = launch_power
        self.bounce_mult = bounce_mult
        self.proj_gravity = proj_gravity
        self.air_resist = air_resist

        self.original_x = self.center_x
        self.original_y = self.center_y
        self.shaking = False

        self.textures = [arcade.load_texture(r"assets\vomba.png", mirrored=True), arcade.load_texture(r"assets\vomba.png")]
        self.set_texture(1)

    def update(self):
        if not self.shaking:
            if not self.is_dead:
                if (self.window.frame + self.creation_frame + 1) % 200 == 0:
                    self.original_x = self.center_x
                    self.original_y = self.center_y
                    self.shaking = True
            super().update()
        else:
            if not self.is_dead:
                _shake_amount = 5
                self.set_position(self.original_x + random.randint(-_shake_amount, _shake_amount), self.original_y + random.randint(-_shake_amount, _shake_amount))
                if (self.window.frame + self.creation_frame + 1) % 200 == TELEGRAPH_FRAMES:
                    self.shaking = False
                    self.fire()
                    self.set_position(self.original_x, self.original_y)
            else:
                self.shaking = False
            Enemy.update(self)

    def fire(self):
        fireball = FireBall()
        fireball.setup(self, self.window, 0, 1, self.target_list, self.damage, self.frame_delay, 0, 0, 0, 0, 1)
        self.window.enemy_projectile_list.append(fireball)
        fireball.throw(self.center_x, self.center_y + 100)


class FireBall(projectile_classes.DamagingProjectile):
    def setup(self, launcher, window, id, boundary_type, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(launcher, window, id, boundary_type, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\vomba projectile.png")]
        self.set_texture(0)
        self.scale = ENEMY_PROJECTILE_SCALE

    def when_retracting(self):
        if self.top < 0:
            self.kill()


class IBall(Enemy):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\iball.png"), arcade.load_texture(r"assets\iball scared.png"), arcade.load_texture(r"assets\iball scared.png", mirrored=True)]
        self.set_texture(0)

    def update(self):
        if not self.is_dead:
            self.movement_logic()
            self.x_vector *= self.friction
            self.y_vector *= self.friction
            self.set_position(self.center_x + self.x_vector, self.center_y + self.y_vector)
        elif self.is_dead:
            self.angle += 20
            self.scale -= self.base_scale/ENEMY_DEAD_FRAMES
            self.alpha = max(0, self.alpha - 255/ENEMY_DEAD_FRAMES)
            if self.die_frame + ENEMY_DEAD_FRAMES == self.window.frame:
                self.top = -2000
                self.kill()
            elif self.die_frame + ENEMY_DEAD_FRAMES < self.window.frame:
                self.kill()
        super().update()

    def movement_logic(self):
        if self.window.player_head.textures.index(self.window.player_head.texture) * 2 - 1 == ((self.window.player_sprite_torso.center_x - self.center_x > 0) - (self.window.player_sprite_torso.center_x - self.center_x < 0)):
            self.radians = math.atan2(self.window.player_sprite_torso.center_y - self.center_y, self.window.player_sprite_torso.center_x - self.center_x)
            self.set_position(self.center_x + self.speed * math.cos(self.radians), self.center_y + self.speed * math.sin(self.radians))
            self.set_texture(0)
        else:
            self.angle = 0
            if self.window.player_sprite_torso.center_x - self.center_x > 0:
                self.set_texture(1)
            else:
                self.set_texture(2)


class MBall(IBall):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\mball.png", mirrored=True), arcade.load_texture(r"assets\mball.png")]
        self.set_texture(1)

    def movement_logic(self):
        if arcade.get_distance_between_sprites(self, self.window.player_sprite_torso) > 200:
            self.radians = math.atan2(self.window.player_sprite_torso.center_y - self.center_y, self.window.player_sprite_torso.center_x - self.center_x)
            self.set_position(self.center_x + self.speed * math.cos(self.radians), self.center_y + self.speed * math.sin(self.radians))
            self.angle = 0
            self.set_texture(self.window.player_sprite_torso.center_x - self.center_x > 0)


class BBall(IBall):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\bball.png")]
        self.set_texture(0)
        self.direction = 0
        self.x_move = 0
        self.y_move = 0

    def movement_logic(self):
        self.direction = math.atan2(self.window.player_sprite_torso.center_y - self.center_y, self.window.player_sprite_torso.center_x - self.center_x) + 0.25 * math.pi
        self.set_position(self.center_x + self.speed * math.cos(self.direction), self.center_y + self.speed * math.sin(self.direction))
        self.angle += 5

    def die(self):
        super().die()
        falling_ball = FallingBBall()
        falling_ball.setup(self.target_list, self.damage * 3, self.frame_delay, self.kb_x, self.kb_y, 2, 0, 1)
        falling_ball.set_position(self.center_x, self.center_y)
        falling_ball.y_vector = 30
        self.window.enemy_projectile_list.append(falling_ball)
        self.top = -2000


class FallingBBall(entity_classes.AttackerSprite):
    def setup(self, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\bball falling.png")]
        self.set_texture(0)
        self.scale = ENEMY_PROJECTILE_SCALE
        self.body_sprite = self

    def update(self):
        super().update()
        self.y_vector -= self.gravity
        self.center_y += self.y_vector

    def when_retracting(self):
        if self.top < 0:
            self.kill()


class CBall(IBall):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\cball.png"), arcade.load_texture(r"assets\cball happy.png")]
        self.set_texture(0)
        self.taken_defense = 0

    def update(self):
        super().update()
        if not self.is_dead:
            if (self.window.frame + self.creation_frame + 1) % 500 == 0:
                self.set_texture(1)
                self.fortune()
            elif (self.window.frame + self.creation_frame + 1) % 500 == TELEGRAPH_FRAMES:
                self.set_texture(0)

    def movement_logic(self):
        if arcade.get_distance_between_sprites(self, self.window.player_sprite_torso) > 600 or arcade.get_distance_between_sprites(self, self.window.player_sprite_torso) < 400:
            self.radians = math.atan2(self.window.player_sprite_torso.center_y - self.center_y, self.window.player_sprite_torso.center_x - self.center_x)
            if arcade.get_distance_between_sprites(self, self.window.player_sprite_torso) < 400:
                self.angle += 180
            self.set_position(self.center_x + self.speed * math.cos(self.radians), self.center_y + self.speed * math.sin(self.radians))
            self.angle = 0

    def fortune(self):
        self.window.player_sprite_torso.defense -= 5
        self.taken_defense += 5

    def die(self):
        super().die()
        self.window.player_sprite_torso.defense += self.taken_defense
        self.taken_defense = 0


class EBall(IBall):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = []
        for i in range(1, 9):
            self.textures.append(arcade.load_texture(f"assets\{str(i)}ball.png"))
        self.set_texture(7)
        self.direction = 0

    def choose_direction(self, x, y, tx, ty):
        margin = 50
        x_same = abs(tx - x) <= margin
        y_same = abs(ty - y) <= margin
        x_is_less = x <= tx
        y_is_less = y <= ty
        if(x_same or y_same) and x_same != y_same:
            if y_same:
                if x_is_less:
                    return 0
                else:
                    return 4
            if x_same:
                if y_is_less:
                    return 2
                else:
                    return 6
        else:
            if x_is_less:
                if y_is_less:
                    return 1
                else:
                    return 7
            else:
                if y_is_less:
                    return 3
                else:
                    return 5

    def movement_logic(self):
        if ((self.left < 0 or self.right > self.window.width) and self.in_game) or ((self.right < 0 or self.left > self.window.width) and not self.in_game) or self.bottom < self.window.player_sprite_torso.ground_y or self.top > self.window.height:
            self.direction = self.choose_direction(self.center_x, self.center_y, self.window.player_sprite_torso.center_x, self.window.player_sprite_torso.center_y) * 45
            self.set_texture(int(self.direction/45))
        self.set_position(self.center_x + self.speed * math.cos(math.radians(self.direction)), self.center_y + self.speed * math.sin(math.radians(self.direction)))

    def attack_register(self, target_sprite):
        reg_damage = self.damage
        self.damage = (self.direction/45 + 1) * (self.damage - target_sprite.defense)
        super().attack_register(target_sprite)
        self.damage = reg_damage


class SDude(WalkingEnemy):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\sword man.png", mirrored=True), arcade.load_texture(r"assets\sword man.png")]
        self.set_texture(1)
        self.weapon = equipment_classes.Weapon()
        self.weapon.setup(target_list, self.damage, self.frame_delay, self.kb_x, self.kb_y, 0, 0, self.strength, self.window, self)
        self.window.enemy_projectile_list.append(self.weapon)
        self.weapon.textures = [arcade.load_texture(r"assets\sword man sword.png")]
        self.weapon.set_texture(0)
        self.target_list = None

    def update(self):
        if self.is_dead:
            self.y_vector -= self.gravity
            self.center_y += self.y_vector
            if self.top < 0:
                self.kill()
        else:
            self.move_weapon()
        super().update()

    def move_weapon(self):
        if self.direction == -1:
            self.weapon.center_x = self.left
        else:
            self.weapon.center_x = self.right
        self.weapon.center_y = self.center_y
        self.weapon.angle = abs(30 - ((self.window.frame - self.creation_frame) % 60)) * -3 * self.direction
        self.weapon.set_position(self.weapon.center_x + self.weapon.height/2 * math.cos(math.radians(self.weapon.angle + 90)), self.weapon.center_y + self.weapon.height/2 * math.sin(math.radians(self.weapon.angle + 90)))

    def die(self):
        super().die()
        self.y_vector = 10
        self.weapon.kill()


class ADude(SDude):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\axe man.png", mirrored=True), arcade.load_texture(r"assets\axe man.png")]
        self.set_texture(1)
        self.weapon = equipment_classes.Weapon()
        self.weapon.setup(target_list, self.damage, self.frame_delay, self.kb_x, self.kb_y, 0, 0, self.strength, self.window, self)
        self.window.enemy_projectile_list.append(self.weapon)
        self.weapon.textures = [arcade.load_texture(r"assets\axe man axe.png")]
        self.weapon.set_texture(0)
        self.target_list = None

    def move_weapon(self):
        if self.direction == -1:
            self.weapon.center_x = self.left
        else:
            self.weapon.center_x = self.right
        self.weapon.center_y = self.center_y
        self.weapon.angle -= 15


class BDude(SDude):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength, launch_power, bounce_mult, proj_gravity, air_resist):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.launch_power = launch_power
        self.bounce_mult = bounce_mult
        self.proj_gravity = proj_gravity
        self.air_resist = air_resist

        self.textures = [arcade.load_texture(r"assets\bow man.png", mirrored=True), arcade.load_texture(r"assets\bow man.png")]
        self.set_texture(1)
        self.weapon = arcade.Sprite()
        self.window.enemy_projectile_list.append(self.weapon)
        self.weapon.textures = [arcade.load_texture(r"assets\bow man bow.png", mirrored=True), arcade.load_texture(r"assets\bow man bow.png")]
        self.weapon.set_texture(1)
        self.original_target_list = target_list
        self.target_list = None

    def move_weapon(self):
        if self.direction == -1:
            self.weapon.center_x = self.left
            self.weapon.set_texture(0)
            self.weapon.angle = -15
        else:
            self.weapon.center_x = self.right
            self.weapon.set_texture(1)
            self.weapon.angle = 15
        self.weapon.center_y = self.center_y
        if (self.window.frame + self.creation_frame + 1) % 150 == 0:
            self.fire()

    def fire(self):
        arrow = Dart()
        arrow.setup(self, self.window, 0, 1, self.original_target_list, self.damage, self.frame_delay, 0, 0, 0, 0, 1)
        self.window.enemy_projectile_list.append(arrow)
        arrow.throw(self.window.player_sprite_torso.center_x, self.window.player_sprite_torso.center_y + 100)


class Dart(projectile_classes.DamagingProjectile):
    def setup(self, launcher, window, id, boundary_type, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(launcher, window, id, boundary_type, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\bow man arrow.png")]
        self.set_texture(0)
        self.scale = ENEMY_PROJECTILE_SCALE

    def when_retracting(self):
        if self.top < 0:
            self.kill()


class DDude(SDude):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\donut man.png", mirrored=True), arcade.load_texture(r"assets\donut man.png")]
        self.set_texture(1)
        self.weapon = equipment_classes.Weapon()
        self.weapon.setup(None, self.damage, self.frame_delay, self.kb_x, self.kb_y, 0, 0, self.strength, self.window, self)
        self.window.enemy_projectile_list.append(self.weapon)
        self.weapon.textures = [arcade.load_texture(r"assets\donut man donut.png"), arcade.load_texture(r"assets\donut man donut eaten.png"), arcade.load_texture(r"assets\donut man donut eaten more.png")]
        self.weapon.set_texture(0)
        self.target_list = None
        self.bite_num = 0

    def move_weapon(self):
        if self.direction == -1:
            self.weapon.center_x = self.left
        else:
            self.weapon.center_x = self.right
        self.weapon.center_y = self.center_y
        interval = 600
        if (self.window.frame + self.creation_frame + 1) % interval < TELEGRAPH_FRAMES:
            self.weapon.angle += 360/TELEGRAPH_FRAMES
            self.weapon.scale = 1 + (30 - abs(30 - ((self.window.frame + self.creation_frame + 1) % interval)))/30
        elif (self.window.frame + self.creation_frame + 1) % interval == TELEGRAPH_FRAMES:
            self.feast()
            self.weapon.angle = 0
            self.weapon.scale = 1

    def feast(self):
        for enemy in self.window.enemy_list:
            enemy.max_hp += self.damage
            enemy.hp += self.damage

        self.bite_num += 1
        if self.bite_num <= 2:
            self.weapon.set_texture(self.bite_num)
        else:
            self.die()


class HDude(SDude):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength):
        super().setup(target_list, body_sprite, window, damage, hp, defense, speed, worth, frame_delay, kb_x, kb_y, gravity, friction, strength)
        self.textures = [arcade.load_texture(r"assets\hammer man.png", mirrored=True), arcade.load_texture(r"assets\hammer man.png")]
        self.set_texture(1)
        self.weapon = equipment_classes.Weapon()
        self.weapon.setup(target_list, self.damage, self.frame_delay, self.kb_x, self.kb_y, 0, 0, self.strength, self.window, self)
        self.window.enemy_projectile_list.append(self.weapon)
        self.weapon.textures = [arcade.load_texture(r"assets\hammer man hammer.png")]
        self.weapon.set_texture(0)
        self.target_list = None
        self.stuck = False
        self.lifting = False

    def update(self):
        if self.is_dead:
            self.y_vector -= self.gravity
            self.center_y += self.y_vector
            if self.top < 0:
                self.kill()
        else:
            self.move_weapon()
        if not self.is_dead:
            self.set_position(self.center_x + self.x_vector + self.speed * self.direction * (90 - abs(self.weapon.angle))/90, self.center_y + self.y_vector)
            if self.left < 0:
                self.direction = 1
                self.set_texture(1)
                self.scale = self.base_scale
            elif self.right > self.window.width:
                self.direction = -1
                self.set_texture(0)
                self.scale = self.base_scale
        Enemy.update(self)

    def move_weapon(self):
        if self.direction == -1:
            self.weapon.center_x = self.left
        else:
            self.weapon.center_x = self.right
        self.weapon.center_y = self.center_y
        if (self.window.player_sprite_torso.center_x - self.center_x)/abs(self.window.player_sprite_torso.center_x - self.center_x) == self.direction and not self.stuck:
            if arcade.get_distance_between_sprites(self, self.window.player_sprite_torso) < 250:
                self.stuck = True
                self.weapon.angle = 0
                self.weapon.angle_change = 3
        drop_speed = 0.1
        if self.stuck:
            self.weapon.angle = abs(self.weapon.angle) + self.weapon.angle_change
            if not self.lifting:
                self.weapon.angle_change += drop_speed
                if self.weapon.angle > 90:
                    self.weapon.angle = 90
                    self.weapon.angle_change = 0
                    self.lifting = True
            else:
                self.weapon.angle_change -= drop_speed
                if self.weapon.angle < 0:
                    self.weapon.angle = 0
                    self.weapon.angle_change = 0
                    self.stuck = False
                    self.lifting = False

        self.weapon.angle = abs(self.weapon.angle) * -self.direction
        self.weapon.set_position(self.weapon.center_x + self.weapon.height / 2 * math.cos(math.radians(self.weapon.angle + 90)),self.weapon.center_y + self.weapon.height / 2 * math.sin(math.radians(self.weapon.angle + 90)))