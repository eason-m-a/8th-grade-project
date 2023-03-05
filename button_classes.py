import arcade, math, equipment_classes, projectile_classes

ICON_SCALE = 1
PAUSE_SCREEN_ALPHA = 0.25
POP_SPEED = 10

def player_has_upgrade(upgrade, window):
    return upgrade in map(lambda upgrade_stuff: upgrade_stuff[0], window.upgrades)

def smooth_pop_update(window, sprite):
    if window.real_frame < sprite.creation_frame + POP_SPEED/2 and window.shop_cycle > 1:
        _smooth_pop_intensity = 0.3
        sprite.scale = ICON_SCALE - _smooth_pop_intensity * math.cos((window.real_frame - sprite.creation_frame)/POP_SPEED * 2 * math.pi) - _smooth_pop_intensity
    else:
        sprite.scale = ICON_SCALE

class UpgradeImg(arcade.Sprite):
    def setup(self, window):
        self.textures = arcade.load_spritesheet("icon sheet.png", 100, 100, 6, 6 * 6)
        self.window = window

    def update(self):
        smooth_pop_update(self.window, self)

class Button(arcade.Sprite):
    def setup(self, window, type):
        self.window = window
        self.type = type

    def press(self):
        if self.type == "x":
            self.window.in_shop = False
            self.window.pause_screen_list[0].alpha = 0
            self.window.upgrade_desc_box_tuple = None
        elif self.type == "s":
            self.window.in_shop = True
            self.window.pause_screen_list[0].alpha = 256 * PAUSE_SCREEN_ALPHA
        for button in self.window.button_list:
            button.flip_alpha()

    def flip_alpha(self):
        if self.alpha == 0:
            self.alpha = 255
        else:
            self.alpha = 0

class ShopButton(Button):
    def setup(self, window, x, y):
        super().setup(window, None)
        self.set_position(x, y - 145 - self.height/2)
        self.textures = [arcade.load_texture("buy button.png"), arcade.load_texture("dont buy button.png")]
        self.set_texture(0)
        self.scale = ICON_SCALE

        self.upgrade_image = UpgradeImg("red pixel.png", 1)
        self.upgrade_image.setup(window)
        self.upgrade_image.set_position(x, y)
        self.window.image_list.append(self.upgrade_image)

        self.cost_box = arcade.Sprite("cost box.png", ICON_SCALE)
        self.cost_box.set_position(x, self.top + self.cost_box.height/2 + 15)
        self.window.shop_box_list.append(self.cost_box)
        self.flip_alpha()

    def update_upgrade(self, upgrade_stuff, texture_index):
        self.upgrade_stuff = upgrade_stuff
        self.creation_frame = self.window.real_frame
        self.upgrade_image.creation_frame = self.window.real_frame
        self.upgrade_image.set_texture(texture_index)
        if self.upgrade_stuff[0] == "closed":
            self.cost_box.alpha = 0
            self.set_texture(1)
        else:
            self.cost_box.alpha = 255
            self.set_texture(0)

    def update(self):
        smooth_pop_update(self.window, self)

    def press(self):
        if self.upgrade_stuff[0] != "closed":
            if self.window.money >= self.upgrade_stuff[1]:
                #if self.upgrade_stuff[1] == max(map(lambda button: button.upgrade_stuff[1], filter(lambda button: button.upgrade_stuff[1] != None, self.window.button_list[2:]))): (if upgrade is most expensive)
                self.window.upgrades.append(self.upgrade_stuff)
                self.window.money -= self.upgrade_stuff[1]
                self.apply_upgrade(self.upgrade_stuff[0])
                self.window.update_shop_buttons()

    def apply_upgrade(self, upgrade):
        if upgrade == "shoes":
            self.window.player_sprite_torso.defense += 1
            for i in range(2):
                shoe = equipment_classes.Shoe()
                shoe.setup(self.window.player_list[3 + i * 2], 0, 0, self.window)
                self.window.clothes_list.append(shoe)
        elif upgrade == "grappling hook":
            grappling_hook = equipment_classes.Grapple()
            grappling_hook.setup(self.window.grappling_hook_launcher, self.window, len(self.window.grappling_hook_list), 2)
            rope = projectile_classes.Rope()
            rope.setup(self.window.grappling_hook_launcher, self.window.grappling_hook_list, len(self.window.grappling_hook_list))
            self.window.grappling_hook_list.append(grappling_hook)
            self.window.rope_list.append(rope)
            grappling_hook.right = 0
        elif upgrade == "more arrows":
            for i in range(2):
                arrow = equipment_classes.Arrow()
                arrow.setup(self.window.bow, self.window, len(self.window.arrow_list), 3, self.window.enemy_list, 20, 0, 0, 0, 0, 1)
                self.window.arrow_list.append(arrow)
        elif upgrade == "sword":
            sword = equipment_classes.Sword()
            sword.setup(self.window.enemy_list, self.window.player_sprite_torso.damage, 30, 20, 20, 0, 0, 1, self.window, self.window.player_sprite_torso)
            self.window.weapon_list.append(sword)
        elif upgrade == "helmet":
            self.window.player_sprite_torso.defense += 3
            helmet = equipment_classes.Hat()
            helmet.setup(self.window.player_head, 0, 0, self.window)
            self.window.clothes_list.append(helmet)
        elif upgrade == "grab crab":
            crab = equipment_classes.Crab()
            crab.set_position(-crab.width/2, 0)
            crab.setup(None, crab, self.window, None, 1, 0, 4, 0, None, None, None, 0.5, 1, 0)
            self.window.friendly_list.append(crab)
        elif upgrade == "bigger head":
            self.window.player_head.base_scale *= 1.5

    def flip_alpha(self):
        if self.alpha == 0:
            self.alpha = 255
            self.upgrade_image.alpha = 255
            if not self.upgrade_stuff[1] == None:
                self.cost_box.alpha = 255
        else:
            self.alpha = 0
            self.upgrade_image.alpha = 0
            self.cost_box.alpha = 0