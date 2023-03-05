import arcade, random, equipment_classes, player_classes, enemy_classes, projectile_classes, entity_classes, button_classes, math, timeit

def player_has_upgrade(upgrade):
    return upgrade in map(lambda upgrade_stuff: upgrade_stuff[0], window.upgrades)

def random_group(enemy_placement):
    if enemy_placement == "random side":
        return ("left", "right", "raid")[random.randint(0, 2)]
    elif enemy_placement == "random drop":
        return ("drop left", "drop right", "drop raid")[random.randint(0, 2)]
    else:
        return ("left", "right", "raid", "drop left", "drop right", "drop raid")[random.randint(0, 5)]

def wave_constructor(enemy_tuples, spawn_delay):
    remaining_enemies = enemy_tuples
    return_list = []
    while remaining_enemies:
        chosen_index = random.randint(0, len(remaining_enemies) - 1)
        enemy_num = random.randint(1, remaining_enemies[chosen_index][2])
        return_list.append([remaining_enemies[chosen_index][0], random_group("random") + remaining_enemies[chosen_index][1], enemy_num, spawn_delay])
        remaining_enemies[chosen_index][2] -= enemy_num
        if remaining_enemies[chosen_index][2] <= 0:
            del remaining_enemies[chosen_index]
    return return_list

SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 864

COIN_SCALE = 1
LAUNCHER_SCALE = 1
ICON_SCALE = 1
HEALTH_BAR_SCALE = 1
MOUSE_SCALE = 1

WHITE_SPACE_BORDER = 5
HEAD_BOB_MOD = 0.5

#damage, hp, defense, speed, worth, frame_delay, kb x, kb y, gravity, friction    launch_power, bounce_mult, gravity, air_resist (30, 0.75, 0.5, 0.99 - launcher ref)
ENEMY_NAME_TO_STATS = {
    "gomba" : (15, 50, 0, 3, 1, 30, 15, 15, 0.5, 0.9),
    "romba" : (4, 300, 20, 2, 2, 30, 20, 15, 0.25, 0.7),
    "bomba" : (50, 1, 0, 7, 0, 30, 25, 25, 0.5, 0.99),
    "jomba" : (20, 150, 3, 4, 4, 30, 20, 20, 0.5, 0.8),
    "vomba" : (30, 250, 5, 1, 6, 30, 15, 10, 1, 0.5, 17, 0, 0.25, 0),
    "iball" : (15, 90, 0, 3, 2, 15, 20, 20, 0, 0.95),
    "mball" : (10, 160, 0, 2, 3, 15, 15, 15, 0, 0.7),
    "bball" : (15, 40, 10, 2.5, 4, 15, 25, 25, 0, 0.99),
    "cball" : (20, 55, 15, 1, 6, 15, 15, 15, 0, 0.85),
    "8ball" : (8, 80, 8, 8, 8, 80, 8, 8, 0, 0.8),
    "sdude" : (25, 40, 5, 5, 5, 20, 15, 0, 0.75, 0.75),
    "adude" : (35, 25, 3, 7, 7, 10, 20, 20, 0.75, 0.75),
    "bdude" : (20, 20, 0, 1, 8, 20, 0, 0, 0.75, 0.75, 15, 0, 0.25, 0.99),
    "ddude" : (20, 55, 0, 3, 10, 30, 10, 10, 0.75, 0.75),
    "hdude" : (50, 50, 10, 4, 12, 30, 30, 5, 0.75, 0.75),
}

UPGRADES = [
["closed", None, "slot closed", ()],
["shoes", 10, "move faster and jump higher and gain 1 defense", ()],
["double jump", 35, "jump again in midair", ()],
["bigger coins", 25, "coins are bigger and are worth 20% more gold", ()],
["grappling hook", 20, "left click to launch a grappling hook that catches coins", ()],
["more arrows", 15, "you can hold two more arrows", ()],
["chocolate coins", 20, "coins have a 20% chance to heal 5 health", ()],
["sword", 20, "spin a sword around you that knocks back enemies", ()],
["helmet", 15, "gain 3 defense", ()],
["grab crab", 20, "walks from side to side while collecting nearby coins", ()],
["bouncy coins", 15, "coins give you a second chance to collect them before they fall off screen", ()],
["bigger head", 30, "shop items cost 5% less and your head is bigger", ()],
["helpful coin", 40, "gain a 10% speed boost for every 100 coins you have (stacks up to 5 times for a 50% speed boost)", ()],
]

class Coin(arcade.Sprite):
    def setup(self):
        self.id = window.coins_created
        self.center_x = random.randint(self.width/2, SCREEN_WIDTH - self.width/2)
        self.bottom = SCREEN_HEIGHT
        self.gravity = -random.randint(4, 10)
        self.y_vector = self.gravity
        self.pulled = False
        self.puller_id = None
        self.random_x_just = None
        self.random_y_just = None
        self.bounce_num = 0
        self.bounce_vector = 20
        self.set_changable_vars()
        self.textures = [arcade.load_texture("coin.png")]
        self.set_texture(0)
        self.scale = COIN_SCALE
        
    def update(self):
        self.set_changable_vars()

        #shake if pulled, fall if not pulled
        if self.pulled:
            if self.random_x_just is None:
                intensity = 20
                self.random_x_just = random.randint(-intensity, intensity)
                self.random_y_just = random.randint(-intensity, intensity)

            self.center_x = window.grappling_hook_list[self.puller_id].center_x + self.random_x_just
            self.center_y = window.grappling_hook_list[self.puller_id].center_y + self.random_y_just - self.height/2
        else:
            #add to y vector if bounced, apply y vector
            if self.bounce_num > 0:
                self.y_vector -= 1
            self.center_y += self.y_vector

        #die if off screen
        if self.bounce_num >= player_has_upgrade("bouncy coins"):
            if self.top <= 0:
                self.die()
        elif self.bottom <= 0:
            #bounce if touching bottom
            self.bounce_num += 1
            self.y_vector = self.bounce_vector
            self.bottom = 1

    def set_changable_vars(self):
        #set variables that change with upgrades
        self.scale = COIN_SCALE * (1 + 0.2 * player_has_upgrade("bigger coins"))
        self.worth = window.wave * (1 + 0.2 * player_has_upgrade("bigger coins"))

    def die(self):
        #kill and give money if on screen
        if self.top > 0:
            window.coins_collected += 1
            window.money += self.worth
            if player_has_upgrade("chocolate coins") and random.randint(1, 5) == 5:
                window.player_sprite_torso.hp += 5
        self.kill()


class Consumable(Coin):
    def setup(self):
        self.id = window.coins_created
        self.center_x = random.randint(self.width / 2, SCREEN_WIDTH - self.width / 2)
        self.bottom = SCREEN_HEIGHT
        self.gravity = -random.randint(3, 5)
        self.y_vector = self.gravity
        self.pulled = False
        self.puller_id = None
        self.random_x_just = None
        self.random_y_just = None
        self.set_changable_vars()
        self.food_type = random.randint(0, 4)
        self.healing = (self.food_type + 1) * 5
        self.textures = [arcade.load_texture("egg.png"), arcade.load_texture("apple.png"), arcade.load_texture("bread.png"), arcade.load_texture("chip bag.png"), arcade.load_texture("steak.png")]
        self.set_texture(self.food_type)
        self.scale = COIN_SCALE

    def update(self):
        self.set_changable_vars()

        #shake if pulled, fall if not pulled
        if self.pulled:
            if self.random_x_just is None:
                intensity = 20
                self.random_x_just = random.randint(-intensity, intensity)
                self.random_y_just = random.randint(-intensity, intensity)

            self.center_x = window.grappling_hook_list[self.puller_id].center_x + self.random_x_just
            self.center_y = window.grappling_hook_list[self.puller_id].center_y + self.random_y_just - self.height / 2
        else:
            #apply y vector
            self.center_y += self.y_vector

        #die if off screen
        if self.top <= 0:
            self.die()
    
    def set_changable_vars(self):
        #set variables that change with upgrades
        pass
    
    def die(self):
        #kill and give money if on screen
        if self.top > 0:
            window.player_sprite_torso.hp += self.healing
        self.kill()


class Game(arcade.Window):
    def __init__(self, width, height, name, fullscreen):
        super().__init__(width, height, name, fullscreen=fullscreen)

    def setup(self):
        #make sprite lists
        self.player_limb_outline_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.friendly_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.clothes_list = arcade.SpriteList()
        self.grappling_hook_list = arcade.SpriteList()
        self.rope_list = arcade.SpriteList()
        self.arrow_list = arcade.SpriteList()
        self.weapon_list = arcade.SpriteList()
        self.launcher_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.enemy_projectile_list = arcade.SpriteList()
        self.button_list = arcade.SpriteList()
        self.pause_screen_list = arcade.SpriteList()
        self.image_list = arcade.SpriteList()
        self.shop_box_list = arcade.SpriteList()
        self.esc_box_list = arcade.SpriteList()
        self.health_bar_list = arcade.SpriteList()
        self.enemy_health_bar_list = arcade.SpriteList()
        self.mouse_list = arcade.SpriteList()
        self.stats_list = arcade.SpriteList()
        self.splash_list = arcade.SpriteList()

        #make fps related vars
        self.frame = 0
        self.real_frame = 0
        self.fps_start_timer = None
        self.fps = None
        self.total_time = 0

        #set window vars
        self.background = arcade.load_texture("background.png")
        self.set_mouse_visible(False)
        self.cursor_image = arcade.Sprite("mouse cursor.png", MOUSE_SCALE)
        self.mouse_list.append(self.cursor_image)

        #make game related vars
        self.lost = False
        self.lose_frame = None
        self.load_screen_duration = 100
        self.wave = 1
        self.wave_start_frame = self.load_screen_duration
        self.most_recent_wave_spawn_frame = self.load_screen_duration
        self.wave_delay = 200
        #make waves
        self.wave_list = [ #omba, ball, dude
            [["8ball", "raid", 1, 100]],
            [["gomba", "raid", 4, 25], ["romba", "reg random", 3, 45]],
            [["gomba", random_group("random drop"), 5, 80], ["gomba", "drop right big", 1, 160], ["romba", "raid", 2, 10], ["gomba", "reg random small", 3, 100], ["iball", "right", 2, 30]],
            [["bomba", random_group("random drop"), 2, 20], ["romba", random_group("random drop"), 3, 30], ["gomba", random_group("random drop"), 4, 40], ["iball", "reg random small", 5, 120]],
            [["gomba", random_group("random side") + "small", 10, 5]] + wave_constructor([["gomba", "", 2], ["romba", "", 3], ["bomba", "small ", 4]], 50),
            [["jomba", "raid", 2, 5]] + wave_constructor([["gomba", "big", 2], ["romba", "", 2], ["romba", "small", 3], ["mball", "", 4]], 30),
            [["jomba", "raid big", 2, 5]] + wave_constructor([["gomba", "small", 5], ["romba", "big", 2], ["bomba", "big", 2], ["vomba", "", 5]], 50),
            wave_constructor([["iball", "small", 5], ["mball", "big", 2], ["bomba", "small", 5], ["sdude", "", 1]],  70),
            [["iball", "right small", 1, 15], ["iball", "right", 1, 15], ["iball", "right big", 1, 15]] + wave_constructor([["mball", "", 5], ["bball", "", 2], ["vomba", "small", 5]], 30),
            [["bball", "raid big", 2, 5]] + wave_constructor([["gomba", "small", 5], ["romba", "big", 10], ["jomba", "", 4], ["vomba", "", 5]], 50),
            wave_constructor([["iball", "small", 5], ["mball", "big", 6], ["bball", "", 4], ["jomba", "small", 5], ["sdude", "big", 3]], 40),
            wave_constructor([["iball", "small", 10], ["cball", "big", 3]], 20),
            wave_constructor([["iball", "", 5], ["mball", "", 3], ["bball", "big", 4], ["cball", "big", 5]], 40),
            wave_constructor([["iball", "small", 5], ["mball", "big", 6], ["bball", "", 4], ["cball", "", 5], ["8ball", "", 5]], 40),
        ]
        self.money = 0
        self.shop_cycle = 1
        self.shop_cycle_penalty = 1.2
        self.coins_collected = 0
        self.coins_created = 0
        self.max_coins = 5
        self.coin_interval = 20
        self.next_coin_spawn_frame = 0
        self.consum_interval = 600
        self.next_consum_spawn_frame = 0
        self.upgrades = []
        self.in_shop = False
        self.cutscene = True
        self.w_held = False
        self.a_held = False
        self.d_held = False
        self.atempting_to_esc = False
        self.upgrade_desc_box_tuple = None

        #create player torso
        self.player_sprite_torso = player_classes.Torso()
        self.player_sprite_torso.ending_y_vector = 20
        self.player_sprite_torso.setup(self.player_sprite_torso, self, 100, 0)
        self.player_list.append(self.player_sprite_torso)

        #create player head
        self.player_head = player_classes.Head()
        self.player_head.setup(self.player_sprite_torso, self, 0, 0)
        self.player_list.append(self.player_head)

        #create player legs
        for a in range(2):
            #create a player leg
            for b in range(2):
                player_sprite_leg = player_classes.Limb()
                player_sprite_leg.setup(self.player_sprite_torso, self, a * 2 - 1, b, a * 2 - 1, 0, 0, 0)
                self.player_list.append(player_sprite_leg)

        #create player arms
        for a in range(2):
            #create a player arm
            for b in range(2):
                player_sprite_arm = player_classes.Limb()
                player_sprite_arm.setup(self.player_sprite_torso, self, a * 2 - 1, b, -(a * 2 - 1), 1, 0, 0)
                self.player_list.append(player_sprite_arm)

        #create player health bar
        health_bar = arcade.Sprite("health bar.png", HEALTH_BAR_SCALE)
        health_bar_backing = arcade.Sprite("red pixel.png", 1)
        health_bar_backing.height = health_bar.height
        health_bar_backing.width = health_bar.width
        health_bar_backing.set_position(SCREEN_WIDTH - 15 - health_bar_backing.width/2, 35)
        self.health_bar_list.append(health_bar_backing)

        health_bar_filling = arcade.Sprite("green pixel.png", 1)
        health_bar_filling.height = health_bar.height
        health_bar_filling.right = SCREEN_WIDTH - 15
        health_bar_filling.center_y = 35
        self.health_bar_list.append(health_bar_filling)

        health_bar_gui = arcade.Sprite("health bar.png", HEALTH_BAR_SCALE)
        health_bar_gui.right = SCREEN_WIDTH - 15
        health_bar_gui.center_y = 35
        self.health_bar_list.append(health_bar_gui)

        #create player's launchers
        self.grappling_hook_launcher = projectile_classes.Launcher("grapple launcher.png", LAUNCHER_SCALE)
        self.grappling_hook_launcher.setup(self.player_sprite_torso, self.grappling_hook_list, 1, 15, 1, 0, 1, 0)
        self.launcher_list.append(self.grappling_hook_launcher)

        self.bow = projectile_classes.Launcher("bow.png", LAUNCHER_SCALE)
        self.bow.setup(self.player_sprite_torso, self.arrow_list, 4, 30, 0.75, 0.5, 0.99, 25)
        self.launcher_list.append(self.bow)
        for i in range(3):
            arrow = equipment_classes.Arrow()
            arrow.setup(self.bow, self, len(self.arrow_list), 3, self.enemy_list, 20, 0, 0, 0, 0, 1)
            self.arrow_list.append(arrow)

        #create buttons to enter/exit shop
        shop_button = button_classes.Button("shop icon.png", ICON_SCALE)
        shop_button.right = SCREEN_WIDTH - WHITE_SPACE_BORDER
        shop_button.top = SCREEN_HEIGHT - WHITE_SPACE_BORDER
        shop_button.setup(self, "s")
        self.button_list.append(shop_button)

        exit_shop_button = button_classes.Button("x icon.png", ICON_SCALE)
        exit_shop_button.right = SCREEN_WIDTH - WHITE_SPACE_BORDER
        exit_shop_button.top = SCREEN_HEIGHT - WHITE_SPACE_BORDER
        exit_shop_button.setup(self, "x")
        exit_shop_button.alpha = 0
        self.button_list.append(exit_shop_button)

        #create buttons to buy upgrades
        X_BUTTON_NUM = 3
        Y_BUTTON_NUM = 2
        X_BORDER = 100
        Y_BORDER = 100
        
        possible_upgrades = []
        for upgrade in UPGRADES[1:7]:
            possible_upgrades.append(upgrade * 1)
        for a in range(Y_BUTTON_NUM):
            _y_pos = (SCREEN_HEIGHT - Y_BORDER * 2) * (a + 0.5)/Y_BUTTON_NUM + Y_BORDER
            for b in range(X_BUTTON_NUM):
                _x_pos = (SCREEN_WIDTH - X_BORDER * 2) * (b + 0.5)/X_BUTTON_NUM + X_BORDER
                _chosen_upgrade_index = random.randint(0, len(possible_upgrades) - 1)
                _upgrade_stuff = possible_upgrades[_chosen_upgrade_index]

                #create button
                button = button_classes.ShopButton()
                button.setup(self, _x_pos, _y_pos)
                button.update_upgrade(_upgrade_stuff, UPGRADES.index(_upgrade_stuff))
                button.cost_box.alpha = 0
                self.button_list.append(button)

                possible_upgrades.remove(_upgrade_stuff)

        #make boxes to hold gui text
        money_box = arcade.Sprite("money box.png", ICON_SCALE)
        money_box.set_position(SCREEN_WIDTH/2, 35)
        self.shop_box_list.append(money_box)

        wave_box = arcade.Sprite("wave box.png", ICON_SCALE)
        wave_box.center_x = money_box.center_x - 410
        wave_box.center_y = money_box.center_y
        self.shop_box_list.append(wave_box)

        fps_box = arcade.Sprite("fps box.png", ICON_SCALE)
        fps_box.left = 0
        fps_box.bottom = 0
        self.shop_box_list.append(fps_box)

        esc_box = arcade.Sprite("confirm esc box.png", 1)
        esc_box.left = 10
        esc_box.top = SCREEN_HEIGHT - 10
        self.esc_box_list.append(esc_box)

        new_wave_box = arcade.Sprite("wave done text.png", 1)
        new_wave_box.set_position(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        new_wave_box.alpha = 0
        self.splash_list.append(new_wave_box)

        #make pause screen sprites
        pause_screen = arcade.SpriteSolidColor(SCREEN_WIDTH + 500, SCREEN_HEIGHT + 500, arcade.color.BLACK)
        pause_screen.set_position(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.pause_screen_list.append(pause_screen)

        instructions = arcade.Sprite("instructions.png", 1)
        instructions.set_position(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.pause_screen_list.append(instructions)

        stats_box = arcade.Sprite("statistics box.png", 1)
        stats_box.left = 625
        stats_box.top = SCREEN_HEIGHT - 10
        self.stats_list.append(stats_box)

    def on_update(self, delta_time: float):
        #update total time
        self.total_time += delta_time

        #update sprite lists above pause screen
        self.mouse_list.update()
        self.pause_screen_list.update()
        self.button_list.update()
        self.image_list.update()
        self.stats_list.update()
        self.health_bar_list.update()
        self.shop_box_list.update()
        self.esc_box_list.update()

        if not self.in_shop and not self.lost:
            #add frame
            self.frame += 1

            #update player stats
            self.player_sprite_torso.speed = self.player_sprite_torso.base_speed
            self.player_sprite_torso.speed *= (1 + 0.3 * (player_has_upgrade("shoes")))
            self.player_sprite_torso.speed *= (1 + min(0.1*(math.floor(self.money/100)), 0.5) * player_has_upgrade("helpful coin"))

            self.player_sprite_torso.jump_speed = self.player_sprite_torso.base_jump_speed
            self.player_sprite_torso.jump_speed *= (1 + 0.2 * (player_has_upgrade("shoes")))

            for weapon in self.weapon_list:
                if weapon.damage != self.player_sprite_torso.damage:
                    weapon.damage = self.player_sprite_torso.damage

            #set player direction and state depending on keys pressed and update limbs
            if self.a_held == self.d_held:
                self.player_sprite_torso.direction = 0
                if self.player_sprite_torso.direction != self.player_sprite_torso.previous_player_direction:
                    self.player_sprite_torso.states[0] = "idle"
            elif self.a_held:
                self.player_sprite_torso.direction = -1
                self.player_head.set_texture(0)
                self.player_head.scale = self.player_head.base_scale
                if self.player_sprite_torso.direction != self.player_sprite_torso.previous_player_direction:
                    self.player_sprite_torso.states[0] = "walking left"
                    self.update_limb_vars()
            elif self.d_held:
                self.player_sprite_torso.direction = 1
                self.player_head.set_texture(1)
                self.player_head.scale = self.player_head.base_scale
                if self.player_sprite_torso.direction != self.player_sprite_torso.previous_player_direction:
                    self.player_sprite_torso.states[0] = "walking right"
                    self.update_limb_vars()

            #if player lets go of or presses a key, update limbs
            if self.player_sprite_torso.direction != self.player_sprite_torso.previous_player_direction:
                self.update_limb_vars()
            self.player_sprite_torso.previous_player_direction = self.player_sprite_torso.direction

            #jump if w is held
            if self.w_held:
                if not self.player_sprite_torso.jumping[0]:
                    self.player_sprite_torso.jumping[0] = True
                    self.player_sprite_torso.y_vector = self.player_sprite_torso.jump_speed

            #apply gravity if player not on ground
            if self.player_sprite_torso.jumping[0]:
                self.player_sprite_torso.y_vector -= self.player_sprite_torso.gravity
            #apply movement to player
            self.player_sprite_torso.center_x += self.player_sprite_torso.x_vector + self.player_sprite_torso.speed * self.player_sprite_torso.direction
            self.player_sprite_torso.center_y += self.player_sprite_torso.y_vector
            #make sure player is in bounds
            self.wall_check(self.player_sprite_torso)

            #bob if the player isnt jumping
            if not self.player_sprite_torso.jumping[0]:
                if "idle" in self.player_sprite_torso.states:
                    #bob slow
                    self.player_sprite_torso.center_y = self.player_sprite_torso.base_y - math.cos((self.frame - self.player_list[2].ani_start_frame)/2 * 360/self.player_list[2].idle_frames * math.pi/180) * self.player_sprite_torso.idle_intensity
                    self.player_head.bottom = self.player_sprite_torso.top - self.player_sprite_torso.idle_intensity * math.cos((self.frame - self.player_list[2].ani_start_frame)/2 * 360/self.player_list[2].idle_frames * math.pi/180) * HEAD_BOB_MOD - self.player_sprite_torso.idle_intensity * HEAD_BOB_MOD
                elif "walking" in self.player_sprite_torso.states[0]:
                    #bob fast
                    self.player_sprite_torso.center_y = self.player_sprite_torso.base_y - math.cos((self.frame - self.player_list[2].ani_start_frame) * 360/self.player_list[2].walk_frames * math.pi/180) * self.player_sprite_torso.idle_intensity
                    self.player_head.bottom = self.player_sprite_torso.top - self.player_sprite_torso.idle_intensity * math.cos((self.frame - self.player_list[2].ani_start_frame) * 360/self.player_list[2].walk_frames * math.pi/180) * HEAD_BOB_MOD - self.player_sprite_torso.idle_intensity * HEAD_BOB_MOD
            else:
                #bob based on player y vector if player is jumping
                self.player_head.bottom = self.player_sprite_torso.top + (math.sin((-self.player_sprite_torso.y_vector + self.player_sprite_torso.jump_speed)/self.player_sprite_torso.jump_speed * math.pi - math.pi/2) - 1) * self.player_sprite_torso.idle_intensity * HEAD_BOB_MOD
                #player isnt jumping if on ground and y vector negative
                if self.player_sprite_torso.center_y <= self.player_sprite_torso.base_y and self.player_sprite_torso.y_vector < 0:
                    self.player_sprite_torso.jumping = [False, False]
                    self.player_sprite_torso.center_y = self.player_sprite_torso.base_y
                    self.player_sprite_torso.y_vector = 0

            coin_hit_list = []
            for body_part in self.player_list:
                coin_hit_list += arcade.check_for_collision_with_list(body_part, self.coin_list)
            coin_hit_list = list(dict.fromkeys(coin_hit_list))
            for coin in coin_hit_list:
                coin.die()

            #update sprite lists below pause screen
            self.player_limb_outline_list.update()
            self.player_list.update()
            self.friendly_list.update()
            self.coin_list.update()
            self.clothes_list.update()
            self.grappling_hook_list.update()
            self.rope_list.update()
            self.arrow_list.update()
            self.weapon_list.update()
            self.launcher_list.update()
            self.enemy_list.update()
            self.enemy_projectile_list.update()
            self.splash_list.update()

            #splash text update
            if self.splash_list[0].alpha > 0:
                self.splash_list[0].alpha -= 255/self.wave_delay

            #make a coin if not loading and room is available
            if self.frame > (self.load_screen_duration + 60):
                if self.frame == self.next_coin_spawn_frame and len(self.coin_list) < self.max_coins:
                    self.coins_created += 1
                    coin = Coin("coin.png", COIN_SCALE)
                    coin.setup()
                    self.coin_list.append(coin)
                if self.frame == self.next_consum_spawn_frame:
                    consumable = Consumable()
                    consumable.setup()
                    self.coin_list.append(consumable)
            if self.frame == (self.frame//self.coin_interval) * self.coin_interval:
                self.next_coin_spawn_frame = (self.frame//self.coin_interval) * self.coin_interval + random.randint(1, self.coin_interval)
            if self.frame == (self.frame//self.consum_interval) * self.consum_interval:
                self.next_consum_spawn_frame = (self.frame//self.consum_interval) * self.consum_interval + random.randint(1, self.consum_interval)

            #update health bar filling
            self.health_bar_list[1].width = 500 * self.player_sprite_torso.hp/self.player_sprite_torso.max_hp
            self.health_bar_list[1].center_x = self.health_bar_list[0].center_x - (500 - 500 * self.player_sprite_torso.hp/self.player_sprite_torso.max_hp)/2

            #spawn enemies
            if any(map(lambda wave: wave != [], self.wave_list)):
                if self.frame >= max(self.most_recent_wave_spawn_frame, self.wave_start_frame) + self.wave_list[0][0][3]:
                    self.create_enemy(self.wave_list[0][0][0], self.wave_list[0][0][1])
                    #reduce enemies in group by 1
                    self.wave_list[0][0][2] -= 1
                    self.most_recent_wave_spawn_frame = self.frame
                    #moves onto next group/wave if there are no enemies in group
                    if self.wave_list[0][0][2] <= 0:
                        del self.wave_list[0][0]
                        if self.wave_list[0] == []:
                            del self.wave_list[0]
                            self.wave += 1
                            self.splash_list[0].alpha = 255
                            self.wave_start_frame = self.frame + self.wave_delay
        else:
            self.pause_screen_list.update()

        if self.lost:
            if self.lose_frame == None:
                self.lose_frame = self.real_frame
                self.player_head.set_texture(2)
                self.player_sprite_torso.jumping[0] = True
            if self.player_head.top < 0:
                self.setup()
            else:
                self.player_sprite_torso.ending_y_vector -= 0.5
            self.player_sprite_torso.center_y += self.player_sprite_torso.ending_y_vector
            self.player_head.bottom = self.player_sprite_torso.top
            self.player_list.update()
            self.clothes_list.update()
            self.weapon_list.update()
            self.launcher_list.update()

        if self.cutscene:
            #fade load screen if frame is greater than duration
            _fade_intensity = 20
            if self.real_frame > self.load_screen_duration:
                self.pause_screen_list[0].alpha = 255 - (self.real_frame - self.load_screen_duration) * _fade_intensity
                self.pause_screen_list[1].alpha = 255 - (self.real_frame - self.load_screen_duration) * _fade_intensity
                if self.pause_screen_list[0].alpha <= 0:
                    self.cutscene = False
                    self.pause_screen_list[0].alpha = 0
                    self.pause_screen_list[1].alpha = 0

    def on_draw(self):
        #calc frame rate
        if self.real_frame % 60 == 0:
            if self.fps_start_timer is not None:
                total_time = timeit.default_timer() - self.fps_start_timer
                self.fps = 60/total_time
            self.fps_start_timer = timeit.default_timer()
        self.real_frame += 1

        arcade.start_render()
        #draw background
        arcade.draw_xywh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        #draw sprite lists below pause screen
        self.coin_list.draw()
        self.friendly_list.draw()
        self.enemy_list.draw()
        self.enemy_projectile_list.draw()
        for body_part in filter(lambda limb: limb.id == None, self.player_list): #draw body
            body_part.draw()
        self.player_limb_outline_list.draw() #draw outline
        for limb in filter(lambda limb: limb.id != None, self.player_list): #draw limbs
            limb.draw()
        self.clothes_list.draw()
        self.rope_list.draw()
        self.grappling_hook_list.draw()
        self.arrow_list.draw()
        self.weapon_list.draw()
        self.launcher_list.draw()
        self.enemy_health_bar_list.draw()
        self.splash_list.draw()

        #draw enemy hp text
        for enemy in self.enemy_list:
            if enemy.hp != enemy.max_hp and not enemy.is_dead:
                if round(enemy.hp, 2) % 1 == 0:
                    hp_display_text = int(round(enemy.hp, 2))
                else:
                    hp_display_text = round(enemy.hp, 2)
                arcade.draw_text(f"{hp_display_text}", enemy.center_x, enemy.health_bar.top + 5, arcade.color.BLACK, font_size=15, anchor_x="center", anchor_y="bottom")

        #draw pause_screen
        self.pause_screen_list.draw()

        #draw gui
        self.shop_box_list.draw()
        if not self.cutscene and not self.lost:
            self.button_list.draw()
            self.health_bar_list.draw()
            self.stats_list.draw()
            arcade.draw_text(f"HP:{round(self.player_sprite_torso.hp, 2)}/{round(self.player_sprite_torso.max_hp, 2)} | DEFENSE:{round(self.player_sprite_torso.defense, 2)} | SPEED:{round(self.player_sprite_torso.speed, 2)} | JUMP POWER:{round(self.player_sprite_torso.jump_speed, 2)}", 635, SCREEN_HEIGHT - 40, arcade.color.BLACK, font_size=20)

        #draw shop stuff
        if self.in_shop:
            self.image_list.draw()
            #draw cost text
            for button in self.button_list[2:]:
                if button.upgrade_stuff[1] != None:
                    arcade.draw_text(f"COSTS {button.upgrade_stuff[1]} COINS", button.cost_box.center_x, button.cost_box.center_y, arcade.color.BLACK, font_size=25, anchor_x="center", anchor_y="center")

        #draw player money text
        if round(self.money, 2) % 1 == 0:
            money_display_text = int(round(self.money, 2))
        else:
            money_display_text = round(self.money, 2)
        arcade.draw_text(f"WAVE:{self.wave}", SCREEN_WIDTH/2 - 410, 35, arcade.color.BLACK, font_size=35, anchor_x="center", anchor_y="center")
        arcade.draw_text(f"COINS:{money_display_text}", SCREEN_WIDTH/2, 35, arcade.color.BLACK, font_size=35, anchor_x="center", anchor_y="center")

        #draw fps text
        if self.fps is not None:
            output = f"FPS: {self.fps:.0f}"
            arcade.draw_text(output, 90, 35, arcade.color.BLACK, font_size=35, anchor_x="center", anchor_y="center")

        #draw upgrade description
        if self.upgrade_desc_box_tuple != None and self.in_shop:
            _box_width = 300
            _box_height = 110
            #background box
            arcade.draw_lrtb_rectangle_filled(self.upgrade_desc_box_tuple[0], self.upgrade_desc_box_tuple[0] + _box_width, self.upgrade_desc_box_tuple[1], self.upgrade_desc_box_tuple[1] - _box_height, arcade.color.BLACK)
            arcade.draw_lrtb_rectangle_filled(self.upgrade_desc_box_tuple[0] + 2, self.upgrade_desc_box_tuple[0] + _box_width - 2, self.upgrade_desc_box_tuple[1] - 2, self.upgrade_desc_box_tuple[1] - _box_height + 2, arcade.color.WHITE)
            description = self.upgrade_desc_box_tuple[2][2]
            line_length = 20
            final_description = ""
            description = description.split(" ")
            char_num = 0
            font_height = 20
            while description:
                for word in description:
                    description = description[1:]
                    char_num += len(word) + 1
                    final_description += word + " "
                    #next line if line_length is exceeded
                    if char_num > line_length:
                        final_description += "\n"
                        char_num = 0
                        break
            #draw text
            output_description = final_description.strip() + "\n"
            arcade.draw_text(f"{output_description}", self.upgrade_desc_box_tuple[0] + 5, self.upgrade_desc_box_tuple[1] - font_height * output_description.count("\n") - font_height - 5, arcade.color.BLACK, font_size=font_height)

        if self.cutscene:
            self.pause_screen_list.draw()

        #draw exit prompt
        if self.atempting_to_esc:
            self.esc_box_list.draw()
            arcade.draw_text("""are you sure you want to exit the game?
press esc again to exit
press any other key (that doesn't affect gameplay) to cancel""", 20, SCREEN_HEIGHT - 60, arcade.color.BLACK, font_size=15, anchor_x="left")

        #draw mouse cursor
        self.mouse_list.draw()

    def on_key_press(self, key, modifiers):
        #movment keys
        if key == arcade.key.W:
            self.w_held = True
            if player_has_upgrade("double jump"):
                if self.player_sprite_torso.jumping[0] and not self.player_sprite_torso.jumping[1]:
                    self.player_sprite_torso.y_vector = self.player_sprite_torso.jump_speed
                    self.player_sprite_torso.jumping[1] = True
        if key == arcade.key.A:
            self.a_held = True
        if key == arcade.key.D:
            self.d_held = True

        #button keys
        if key == arcade.key.F and not self.cutscene and not self.lost:
            if self.in_shop:
                self.button_list[1].press()
            else:
                self.button_list[0].press()
        if key == arcade.key.ESCAPE:
            if self.atempting_to_esc:
                self.close()
            self.atempting_to_esc = True
        if key not in (arcade.key.W, arcade.key.A, arcade.key.D, arcade.key.F, arcade.key.I, arcade.key.ESCAPE) and self.atempting_to_esc:
            self.atempting_to_esc = False

        #debug
        if key == arcade.key.P:
            print(f"average fps of {self.real_frame/self.total_time}")

    def on_key_release(self, key, modifiers):
        #movement keys
        if key == arcade.key.W:
            self.w_held = False
        if key == arcade.key.A:
            self.a_held = False
        if key == arcade.key.D:
            self.d_held = False

    def on_mouse_motion(self, x, y, dx, dy):
        #move cursor
        self.cursor_image.left = x
        self.cursor_image.top = y

        self.check_for_hover(x, y)

    def on_mouse_press(self, x, y, click_type, modifiers):
        _pressed_ui_button = False
        #left click and game has officialy started
        if click_type == 1 and not self.cutscene and not self.lost:
            #press every visible button
            for button in filter(lambda button: button.alpha == 255, self.button_list):
                if button.center_x - button.width/2 * 1/button.scale <= x and button.center_x + button.width/2 * 1/button.scale >= x and button.center_y - button.height/2 * 1/button.scale <= y and button.center_y + button.height/2 * 1/button.scale >= y and (self.in_shop or button.type == "s"):
                    button.press()
                    _pressed_ui_button = True
                    break

        #if a shop button wasnt pressed and not in shop
        if not self.in_shop and not _pressed_ui_button:
            #launch projectiles for every launcher, max 1 per launcher
            for launcher in self.launcher_list:
                if click_type == launcher.button_type:
                    for projectile in launcher.projectile_list:
                        if not projectile.thrown:
                            self.player_sprite_torso.states[1] = "launching"
                            self.update_limb_vars()
                            projectile.throw(x, y)
                            launcher.adjust_angle(projectile)
                            break

    def check_for_hover(self, x, y):
        if self.in_shop:
            #if button visible and mouse within its bounds, hover var is set to buttons vars
            for button in filter(lambda button: button.alpha == 255, self.button_list):
                if button.center_x - button.width/2 * 1/button.scale <= x and button.center_x + button.width/2 * 1/button.scale >= x and button.center_y - button.height/2 * 1/button.scale <= y and button.center_y + button.height/2 * 1/button.scale >= y:
                    self.upgrade_desc_box_tuple = (x, y, button.upgrade_stuff)
                    break
                else:
                    self.upgrade_desc_box_tuple = None

    def wall_check(self, sprite):
        #makes a sprite go in bounds of screen
        if sprite.left < 0:
            sprite.left = 0
            sprite.x_vector = abs(sprite.x_vector) * 0.5
        if sprite.right > SCREEN_WIDTH:
            sprite.right = SCREEN_WIDTH
            sprite.x_vector = abs(sprite.x_vector) * -0.5

    def update_limb_vars(self):
        #set all limbs' player state and anim start frame
        for limb in filter(lambda limb: limb.id != None, self.player_list):
            limb.set_anim_vars(self.frame)

    def update_shop_buttons(self):
        #inc shop cycle
        self.shop_cycle += 1

        #set possible upgrades
        possible_upgrades = []
        for upgrade in UPGRADES[1:]:
            possible_upgrades.append(upgrade * 1)

        for upgrade_name in map(lambda upgrade_stuff: upgrade_stuff[0], self.upgrades):
            del possible_upgrades[list(map(lambda upgrade_stuff: upgrade_stuff[0], possible_upgrades)).index(upgrade_name)]

        if len(possible_upgrades) < 6:
            for i in range(6 - len(possible_upgrades)):
                possible_upgrades.append(UPGRADES[0])

        #set upgrade stuff
        for index, button in enumerate(self.button_list[2:]):
            _chosen_upgrade_index = random.randint(0, len(possible_upgrades) - 1)
            _upgrade_stuff = possible_upgrades[_chosen_upgrade_index] * 1
            if _upgrade_stuff[1] != None:
                if player_has_upgrade("bigger head"):
                    _upgrade_stuff[1] *= 0.95
                _upgrade_stuff[1] = round(_upgrade_stuff[1] * self.shop_cycle_penalty ** (self.shop_cycle - 1))
            button.update_upgrade(_upgrade_stuff, UPGRADES.index(possible_upgrades[_chosen_upgrade_index]))
            possible_upgrades.remove(possible_upgrades[_chosen_upgrade_index])
            self.check_for_hover(self.upgrade_desc_box_tuple[0], self.upgrade_desc_box_tuple[1])

    def create_enemy(self, enemy_type, modifiers):
        #create enemy
        stats = ENEMY_NAME_TO_STATS[enemy_type]

        if "this code is messy": #click the down arrow to not show this
            if enemy_type == "gomba":
                enemy = enemy_classes.Gomba()
            elif enemy_type == "romba":
                enemy = enemy_classes.Romba()
            elif enemy_type == "bomba":
                enemy = enemy_classes.Bomba()
            elif enemy_type == "jomba":
                enemy = enemy_classes.Jomba()
            elif enemy_type == "vomba":
                enemy = enemy_classes.Vomba()
            elif enemy_type == "iball":
                enemy = enemy_classes.IBall()
            elif enemy_type == "mball":
                enemy = enemy_classes.MBall()
            elif enemy_type == "bball":
                enemy = enemy_classes.BBall()
            elif enemy_type == "cball":
                enemy = enemy_classes.CBall()
            elif enemy_type == "8ball":
                enemy = enemy_classes.EBall()
            elif enemy_type == "sdude":
                enemy = enemy_classes.SDude()
            elif enemy_type == "adude":
                enemy = enemy_classes.ADude()
            elif enemy_type == "bdude":
                enemy = enemy_classes.BDude()
            elif enemy_type == "ddude":
                enemy = enemy_classes.DDude()
            elif enemy_type == "hdude":
                enemy = enemy_classes.HDude()

        x = 0
        y = 0
        enemy_margin = 250
        if "right" in modifiers:
            x = SCREEN_WIDTH + enemy.width/2 + enemy_margin
        elif "left" in modifiers:
            x = -enemy.width/2 - enemy_margin
        elif "raid" in modifiers:
            x = SCREEN_WIDTH * (self.wave_list[0][0][2] % 2 == 0) + (enemy.width/2 + enemy_margin) * ((self.wave_list[0][0][2] % 2 == 0) * 2 - 1)

        if "drop" in modifiers:
            y = SCREEN_HEIGHT + enemy.height/2

        if "reg random" in modifiers:
            possible_spawn_poses = ((-enemy.width/2 - enemy_margin, SCREEN_HEIGHT + enemy.height/2), (SCREEN_WIDTH + enemy.width/2 + enemy_margin, SCREEN_HEIGHT + enemy.height/2), (-enemy.width/2 - enemy_margin, 0), (SCREEN_WIDTH + enemy.width/2 + enemy_margin, 0))
            random_index = random.randint(0, 3)
            x = possible_spawn_poses[random_index][0]
            y = possible_spawn_poses[random_index][1]
        x = SCREEN_WIDTH/2
        y = SCREEN_HEIGHT/2
        enemy.set_position(x, y)

        #damage, hp, defense, speed, worth, frame_delay, kb x, kb y, gravity, friction    launch_power, bounce_mult, gravity, air_resist
        if len(stats) == 10:
            enemy.setup(self.player_list, enemy, self, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8], stats[9], 1)
        else:
            enemy.setup(self.player_list, enemy, self, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8], stats[9], 1, stats[10], stats[11], stats[12], stats[13])

        #add modifiers
        if "big" in modifiers:
            enemy.base_scale = 1.5
            enemy.damage *= 1.5
            enemy.max_hp *= 3
            enemy.hp *= 3
            enemy.gravity *= 1.25
            enemy.friction *= 0.5
        elif "small" in modifiers:
            enemy.base_scale = 0.75
            enemy.damage *= 0.5
            enemy.speed *= 2
            enemy.max_hp *= 0.5
            enemy.hp *= 0.5
            enemy.gravity *= 0.75
            enemy.friction += (1 - enemy.friction) * 0.5
        enemy.scale = enemy.base_scale

        self.enemy_list.append(enemy)


window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, "coin get game", fullscreen=1)
window.setup()
arcade.run()