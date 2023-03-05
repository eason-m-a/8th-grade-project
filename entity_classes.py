import arcade

class AttackerSprite(arcade.Sprite):
    def setup(self, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength):
        self.target_list = target_list
        self.damage = damage
        self.frame_delay = frame_delay
        self.kb_x = kb_x
        self.kb_y = kb_y
        self.gravity = gravity
        self.friction = friction
        self.strength = strength

    def update(self):
        if self.target_list != None:
            hit_list = map(lambda sprite_part: sprite_part.body_sprite, arcade.check_for_collision_with_list(self, self.target_list))
            hit_list = list(dict.fromkeys(hit_list))
            for hit_sprite in hit_list:
                self.attack(hit_sprite.body_sprite)

    def attack(self, target_sprite):
        if not self.body_sprite in map(lambda tup: tup[0], target_sprite.invincibility_list) and not target_sprite.is_dead and self.alpha != 0:
            self.attack_register(target_sprite)

    def attack_register(self, target_sprite):
        target_sprite.body_sprite.x_vector = self.kb_x * (((target_sprite.center_x - self.center_x) > 0) * 2 - 1)
        target_sprite.body_sprite.y_vector = self.kb_y * (((target_sprite.center_y - self.center_y) > 0) * 2 - 1)
        if (self.damage * self.strength - target_sprite.defense) * ((self.damage * self.strength - target_sprite.defense) >= 0) != 0:
            target_sprite.body_sprite.hp -= (self.damage * self.strength - target_sprite.defense) * ((self.damage * self.strength - target_sprite.defense) >= 0)
            target_sprite.body_sprite.on_hurt(self.body_sprite)


class DamagableSprite(arcade.Sprite):
    def setup(self, body_sprite, window, hp, defense):
        self.body_sprite = body_sprite
        self.invincibility_list = []
        self.window = window
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.is_dead = False
        self.die_frame = None

    def update(self):
        if not self.is_dead:
            for invincibility_tuple in filter(lambda invincibility_tuple: self.window.frame >= invincibility_tuple[1] + invincibility_tuple[0].frame_delay, self.invincibility_list):
                self.invincibility_list.remove(invincibility_tuple)

    def on_hurt(self, attacker):
        if not self.is_dead:
            self.invincibility_list.append((attacker.body_sprite, self.window.frame))


class DamagableAttacker(AttackerSprite, DamagableSprite):
    def setup(self, target_list, body_sprite, window, damage, hp, defense, frame_delay, kb_x, kb_y, gravity, friction, strength):
        AttackerSprite.setup(self, target_list, damage, frame_delay, kb_x, kb_y, gravity, friction, strength)
        DamagableSprite.setup(self, body_sprite, window, hp, defense)

    def update(self):
        if not self.is_dead:
            AttackerSprite.update(self)
            DamagableSprite.update(self)