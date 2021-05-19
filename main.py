import pyxel
from random import randint
from random import choice

# Zombies' class
zombie_source_map = {"NormalZombies": (1, 0, 0, 16, 16, 0),  # [img, u, v, w, h, [colkey]]
                     "FlagZombies": (1, 0, 80, 16, 16, 0),
                     "ConeHeadZombies": (1, 0, 16, 16, 16, 0),
                     "BucketHeadZombies": (1, 0, 32, 16, 16, 0),
                     "NewspaperZombies": (1, 0, 48, 16, 16, 0),
                     "ScreenDoorZombies": (1, 0, 96, 16, 16, 0)}
zombie_extra_health_map = {"NormalZombies": 0,
                           "FlagZombies": 0,
                           "ConeHeadZombies": 370,
                           "BucketHeadZombies": 1100,
                           "NewspaperZombies": 150,
                           "ScreenDoorZombies": 1100}


class Zombies:
    def __init__(self, set_type, extra_health, x, y):
        self.type = set_type
        self.is_alive = True    # can absorb damage if alive
        self.eat = False
        self.health = extra_health + 270
        self.x = x
        self.y = y
        self.slow_time = 0
        self.speed = -0.2       # going from right to left
        self.source = zombie_source_map[self.type]
        self.should_pop = False
        self.death_animation_timer = 3 * 20
        self.damage = 1.5  # when eating plants, produce 1 damage each frame (20 damage/second)

        self.blast = False
        self.eaten_by_chomper = False

    def set_animation(self):
        if self.is_alive:
            # eat animation
            if not self.eat:
                offset = 0
            else:
                offset = 0 if pyxel.frame_count % 10 == 0 else 16
            # animation when absorbing damage
            if 270 < self.health:
                temp = [i for i in zombie_source_map[self.type]]
                temp[1] += offset
                self.source = temp
            elif 150 < self.health <= 270:
                if self.type == "NewspaperZombies":
                    self.source = [1, 0 + offset, 48, 16, 16, 0]  # [img, u, v, w, h, [colkey]]
                elif self.type == "FlagZombies":
                    self.source = self.source = [1, 0 + offset, 80, 16, 16, 0]
                else:
                    self.source = [1, 0 + offset, 0, 16, 16, 0]
            elif 40 < self.health <= 150:
                if self.type == "NewspaperZombies":
                    self.source = [1, 0 + offset, 64, 16, 16, 0]
                else:
                    self.source = [1, 48 + offset, 0, 16, 16, 0]
            else:
                self.health -= 1
                self.source = [1, 48 + offset, 16, 16, 16, 0]

    def move(self):
        if self.health <= 0:
            self.is_alive = False
        if self.is_alive:
            if not self.eat:
                if self.slow_time > 0:
                    self.slow_time -= 1
                    self.speed = -0.1 if not (self.type == "NewspaperZombies" and 40 < self.health <= 150) else -0.2
                else:
                    self.slow_time = 0
                    self.speed = -0.2 if not (self.type == "NewspaperZombies" and 40 < self.health <= 150) else -0.25
                self.x += self.speed
                if self.slow_time > 0:
                    self.slow_time -= 1
            else:
                self.speed = 0  # cannot move when eating
            self.set_animation()
        else:
            if self.eaten_by_chomper:
                self.should_pop = True
            else:
                # death animation
                self.death_animation_timer -= 1
                if 40 < self.death_animation_timer <= 60:
                    self.source = (1, 48, 32, 16, 16, 0) if not self.blast else (1, 48, 64, 16, 16, 7)
                elif 20 < self.death_animation_timer <= 40:
                    self.source = (1, 48, 48, 16, 16, 0) if not self.blast else (1, 48, 80, 16, 16, 7)
                elif 0 < self.death_animation_timer <= 20:
                    self.source = (1, 48, 48, 16, 16, 0) if not self.blast else (1, 48, 96, 16, 16, 7)
                else:
                    self.should_pop = True

    def absorb_effect(self, damage, slow_time):
        if self.is_alive:
            self.health -= damage
            if slow_time == 100:
                self.slow_time = slow_time

    def draw(self):
        pyxel.blt(self.x, self.y, *self.source)


# Plants' class
plant_source_map = {"Peashooter": (0, 16, 16, 16, 16, 13),  # [img, u, v, w, h, [colkey]]
                    "SunFlower": (0, 16, 32, 16, 16, 13),
                    "CherryBomb": (0, 16, 48, 16, 16, 13),
                    "WallNut": (0, 16, 64, 16, 16, 13),
                    "SnowPea": (0, 16, 80, 16, 16, 13),
                    "Chomper": (0, 16, 96, 16, 16, 13)}
plant_damage_map = {"Peashooter": 20,  # dps
                    "SunFlower": 0,
                    "CherryBomb": 1800,
                    "WallNut": 0,
                    "SnowPea": 20,
                    "Chomper": 1400}
plant_selection_map = {1: "Peashooter",  # select plant using mouse's x_index
                       2: "SunFlower",
                       3: "CherryBomb",
                       4: "WallNut",
                       5: "SnowPea",
                       6: "Chomper"}
plant_reset_counter_map = {"Peashooter": 30,  # frames
                           "SunFlower": 200,
                           "CherryBomb": None,
                           "WallNut": None,
                           "SnowPea": 30,
                           "Chomper": None}
plant_cost_cd_map = {"Peashooter": (100, 100),  # (cost, cd)
                     "SunFlower": (50, 100),  # 5 sec
                     "CherryBomb": (150, 300),  # 20 sec
                     "WallNut": (50, 200),  # 10 sec
                     "SnowPea": (175, 140),  # 7 sec
                     "Chomper": (150, 140)}
plant_card_map = {"Peashooter": (0, 16, 112, 16, 16),  # [img, u, v, w, h]
                  "SunFlower": (0, 16, 128, 16, 16),
                  "CherryBomb": (0, 16, 144, 16, 16),
                  "WallNut": (0, 16, 160, 16, 16),
                  "SnowPea": (0, 16, 176, 16, 16),
                  "Chomper": (0, 16, 192, 16, 16)}


class EdiblePlants:
    def __init__(self, typ, x, y):
        if typ == "WallNut":
            self.health = 4000
        else:
            self.health = 60
        self.x = x
        self.y = y
        self.type = typ
        self.source = [x, y, *plant_source_map[typ]]
        self.damage = plant_damage_map[typ]
        self.is_alive = True

        self.do_skill_signal = False
        if self.type == "Peashooter" or self.type == "SnowPea":
            self.do_skill_counter = 15
        else:
            self.do_skill_counter = plant_reset_counter_map[self.type]

        self.digesting = False
        self.digest_counter = 40 * 20
        self.eat_ani_counter = 20  # frames

    def __str__(self):
        return self.type

    def signal_counter(self, zom_list):
        if self.do_skill_counter is None:
            return
        if self.type == "SunFlower":
            if self.do_skill_counter > 0:
                self.do_skill_counter -= 1
                if self.do_skill_counter == 0:
                    self.do_skill_signal = True
            else:
                self.do_skill_counter = 200  # for sunflower
                self.do_skill_signal = False
        elif self.type == "Peashooter" or self.type == "SnowPea":
            trigger_condition = False
            for zom in zom_list:
                if zom.x > self.x + 8:
                    trigger_condition = True
                    break
            if trigger_condition:
                if self.do_skill_counter > 0:
                    self.do_skill_counter -= 1
                    if self.do_skill_counter == 0:
                        self.do_skill_signal = True
                else:
                    self.do_skill_signal = False
                    self.do_skill_counter = plant_reset_counter_map[self.type]
            else:
                self.do_skill_signal = False
                self.do_skill_counter = plant_reset_counter_map[self.type]

    def get_skill(self):  # for shooter and sunflower
        if self.type == "Peashooter" or self.type == "SnowPea":
            return Bullet(self.x + 10, self.y, self.type)
        elif self.type == "SunFlower":
            if self.y + 16 <= pyxel.height - 16:
                upperbound = self.y + 16
            else:
                upperbound = self.y + 4
            return Sun(self.x + 8, self.y - 4, randint(self.y, upperbound))
        else:
            return None

    def get_hurt(self, damage):
        self.health -= damage
        if self.type == "WallNut":
            if self.health < 4000 / 2:
                self.source = [self.x, self.y, *[0, 32, 64, 16, 16, 13]]
        if self.health <= 0:
            self.is_alive = False

    # method for chomper only
    def chomper_animation(self, eat_trigger):  # eat_trigger there is an alive zombie in the front
        if not self.digesting:
            self.source = [self.x, self.y, 0, 16, 96, 16, 16, 13]
            if eat_trigger:
                self.source = [self.x, self.y, 0, 32, 96, 16, 16, 13]
                self.eat_ani_counter -= 1
                if self.eat_ani_counter == 0:
                    self.source = [self.x, self.y, 0, 48, 96, 16, 16, 13]
                    self.digesting = True
                    self.eat_ani_counter = 20
                    return self.damage
        else:
            self.source = [self.x, self.y, 0, 48, 96, 16, 16, 13]
            self.digest_counter -= 1
            if self.digest_counter == 0:
                self.digesting = False
                self.digest_counter = 40 * 20
                self.source = [self.x, self.y, 0, 16, 96, 16, 16, 13]


class CherryBomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.source = [self.x, self.y, *plant_source_map["CherryBomb"]]
        self.damage = plant_damage_map["CherryBomb"]
        self.bla_counter = 60  # 2 + 1 sec
        self.should_pop = False
        self.expl_xreg = [self.x - 16, self.x + 32]  # range of x

    def blast_animation(self):
        if 40 < self.bla_counter <= 60:
            self.source = [self.x, self.y, *plant_source_map["CherryBomb"]]
        elif 20 < self.bla_counter <= 40:
            self.source[3] = 32
        elif 0 < self.bla_counter <= 20:
            self.source = [self.x - 16, self.y - 16, 0, 96, 0, 48, 48, 13]
        else:
            self.should_pop = True
        self.bla_counter -= 1


# tools' class
class Bullet:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.damage = 0
        self.slow_time = 0 * 20
        self.hit_obj = False
        self.pop_counter = 3  # frames
        self.to_pop = False

        if type == "Peashooter":  # (x, y, img, u, v, w, h, [colkey])
            self.source = [self.x, self.y, 0, 32, 16, 16, 16, 13]
        else:  # SnowPea
            self.source = [self.x, self.y, 0, 32, 80, 16, 16, 13]

    def update(self, zom_pos):
        if self.x + 1.2 < zom_pos:
            self.x += 1
            self.source[0] += 1
        else:
            self.x = zom_pos
            self.source[0] = zom_pos
            self.source[3] = 48
            self.damage = plant_damage_map["Peashooter"]
            if self.type == "SnowPea":
                self.slow_time = 5 * 20  # frames
            self.hit_obj = True
        if self.hit_obj:
            self.x = zom_pos
            self.source[0] = zom_pos
            self.pop_counter -= 1
            if self.pop_counter <= 0:
                self.to_pop = True
        return [self.damage, self.slow_time]  # damage, slow_time


class Sun:
    def __init__(self, x, y, pos):
        self.x = x
        self.y = y
        self.still_y_pos = pos
        self.still = False
        self.source = [self.x, self.y, 0, 32, 32, 16, 16, 13]

    def fall_down(self):
        if self.y >= self.still_y_pos:
            self.still = True
        if not self.still:
            self.y += 0.5
            self.source[1] = self.y


class Car:
    def __init__(self, y):
        self.x = 16
        self.y = y
        self.source = (0, 32, 0, 16, 16, 0)  # (img, u, v, w, h, [colkey])
        self.active = False

    def run(self):
        self.x += 2  # speed is 2 px/frame


class App:
    def __init__(self):
        pyxel.init(188, 112, caption="Plants vs Zombies", fps=20)
        pyxel.load("my_resource.pyxres")
        pyxel.mouse(True)

        self.sun_num = 50  # number of sunlight collected
        self.wave_number = 0
        self.time = 0  # start from 0s
        self.self_pro_sun_counter = 300  # 15 sec
        self.lose = False

        self.selected_box = None  # box to show selection
        self.hover_box = None
        self.selected_type = None  # [img, u, v, w, h, [colkey]]

        self.plants_cd = {"Peashooter": [0, True], "SunFlower": [0, True],
                          "CherryBomb": [0, True], "WallNut": [0, True],
                          "SnowPea": [0, True], "Chomper": [0, True]}  # [t, ready]
        self.sun_list = []
        self.lines = {0: {"car": Car(2 * 8), "plants": {}, "zombies": [], "bullets": [], "bomb": []},
                      1: {"car": Car(4 * 8), "plants": {}, "zombies": [], "bullets": [], "bomb": []},
                      2: {"car": Car(6 * 8), "plants": {}, "zombies": [], "bullets": [], "bomb": []},
                      3: {"car": Car(8 * 8), "plants": {}, "zombies": [], "bullets": [], "bomb": []},
                      4: {"car": Car(10 * 8), "plants": {}, "zombies": [], "bullets": [], "bomb": []},
                      5: {"car": Car(12 * 8), "plants": {}, "zombies": [], "bullets": [],"bomb": []}}

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if self.lose:
            if pyxel.btnp(pyxel.KEY_R):
                self.__init__()
            return

        if pyxel.frame_count % 20 == 0 and pyxel.frame_count != 0:
            self.time += 1  # update game time

        for cd in self.plants_cd.values():  # cd counter
            if not cd[1]:  # not ready
                if cd[0] > 0:
                    cd[0] -= 1
                else:  # cd[0] == 0
                    cd[1] = True

        self.self_producing_sun()

        # update sunlight
        for s in self.sun_list:
            if s.x <= pyxel.mouse_x <= s.x + 16 and s.y <= pyxel.mouse_y <= s.y + 16:
                self.sun_num += 50 if self.sun_num + 50 <= 9999 else 0
                self.sun_list.pop(self.sun_list.index(s))
            else:
                s.fall_down()

        for line in range(6):
            # update bullets and first zombie in front of them
            for bul in self.lines[line]["bullets"]:
                if self.lines[line]["zombies"] != []:
                    # find the first zombie in front of the bullet
                    first_zom_idx = None
                    for zom in self.lines[line]["zombies"]:
                        if not zom.is_alive or zom.x < bul.x:
                            continue
                        if not bul.hit_obj:
                            if first_zom_idx is None:
                                first_zom_idx = self.lines[line]["zombies"].index(zom)
                                continue
                            if bul.x < zom.x < self.lines[line]["zombies"][first_zom_idx].x:
                                first_zom_idx = self.lines[line]["zombies"].index(zom)
                        else:
                            if zom.x == bul.x:
                                first_zom_idx = self.lines[line]["zombies"].index(zom)
                            else:
                                continue

                    if first_zom_idx is not None and not bul.to_pop:
                        d, st = bul.update(self.lines[line]["zombies"][first_zom_idx].x)
                        self.lines[line]["zombies"][first_zom_idx].absorb_effect(d, st)
                    if first_zom_idx is None and not bul.to_pop:
                        bul.update(pyxel.width)
                else:
                    bul.update(pyxel.width)

                if bul.to_pop or bul.x >= pyxel.width:
                    self.lines[line]["bullets"].pop(self.lines[line]["bullets"].index(bul))

            # update cars
            if self.lines[line]["car"].active:
                if not self.lines[line]["car"].x > 232:  # away from the edge of the window
                    self.lines[line]["car"].run()

            # cherry bomb explode damage
            for che in self.lines[line]["bomb"]:
                if che.should_pop:
                    self.lines[line]["bomb"].pop(self.lines[line]["bomb"].index(che))
                    continue
                che.blast_animation()
                if che.bla_counter == 20:
                    l = [i for i in range(6) if int(che.y / 16) - 2 <= i <= int(che.y / 16)]
                    for li in l:
                        for zom in self.lines[li]["zombies"]:
                            if int(zom.x) in range(che.expl_xreg[0], che.expl_xreg[1] + 1):
                                zom.health -= che.damage
                                zom.is_alive = False
                                zom.blast = True

            # update zombies and plants
            for zom in self.lines[line]["zombies"]:
                if zom.is_alive and zom.x <= 0:
                    self.lose = True
                    break
                if zom.should_pop:
                    self.lines[line]["zombies"].pop(self.lines[line]["zombies"].index(zom))
                    continue
                if int((zom.x + 5) / 16) - 2 in self.lines[line]["plants"].keys():
                    zom.eat = True
                    self.lines[line]["plants"][int((zom.x + 5) / 16) - 2].get_hurt(zom.damage)
                    if not self.lines[line]["plants"][int((zom.x + 5) / 16) - 2].is_alive:
                        del self.lines[line]["plants"][int((zom.x + 5) / 16) - 2]
                else:
                    zom.eat = False
                if self.lines[line]["car"].x <= int(zom.x) <= self.lines[line]["car"].x + 8:
                    self.lines[line]["car"].active = True  # hit cars
                    zom.health = 0
                zom.move()

        # Add bullets and sunlight
        for line in range(6):
            for pla in self.lines[line]["plants"].values():
                if pla.type == "Chomper":
                    # find the first zombie in front of the chomper
                    first_zom_idx = None
                    for zom in self.lines[line]["zombies"]:
                        if not zom.is_alive or zom.x < pla.x or zom.x > pla.x + 28:
                            continue
                        if first_zom_idx is None:
                            first_zom_idx = self.lines[line]["zombies"].index(zom)
                            continue
                        if pla.x < zom.x < self.lines[line]["zombies"][first_zom_idx].x:
                            first_zom_idx = self.lines[line]["zombies"].index(zom)
                    damage = pla.chomper_animation(first_zom_idx is not None)
                    if damage is not None:
                        self.lines[line]["zombies"][first_zom_idx].health -= damage
                        self.lines[line]["zombies"][first_zom_idx].eaten_by_chomper = True
                else:
                    pla.signal_counter(self.lines[line]["zombies"])
                    if pla.signal_counter is not None and pla.do_skill_signal is True:
                        if pla.type != "SunFlower":
                            self.lines[line]["bullets"].append(pla.get_skill())  # bullet
                        else:
                            self.sun_list.append(pla.get_skill())

        self.mouse_reaction()
        self.next_wave()

    def draw(self):
        if self.lose:
            pyxel.blt(55, 17, 2, 0, 0, 80, 80, 7)
            pyxel.mouse(False)
            s = "Press R to restart"
            pyxel.text(60, 100, s, 0)
            return

        pyxel.bltm(0, 0, 0, 0, 0, 112, 152)

        # draw plants' cards
        for i, t in enumerate(list(plant_card_map.keys())):
            img, u, v, w, h = plant_card_map[t]
            if self.plants_cd[t][1]:
                pyxel.blt((i + 1) * 16, 0, img, u, v, w, h)
            else:
                if 0.666 < self.plants_cd[t][0] / plant_cost_cd_map[t][1] <= 1:
                    pyxel.blt((i + 1) * 16, 0, img, u + 16, v, w, h)
                elif 0.333 < self.plants_cd[t][0] / plant_cost_cd_map[t][1] <= 0.666:
                    pyxel.blt((i + 1) * 16, 0, img, u + 32, v, w, h)
                else:
                    pyxel.blt((i + 1) * 16, 0, img, u + 48, v, w, h)

        if self.selected_box is not None:
            pyxel.blt(*self.selected_box)
        if self.hover_box is not None:
            pyxel.blt(*self.hover_box)

        s = "{:^4}".format(self.sun_num)
        pyxel.text(1, 17, s, 0)

        # draw sunlight
        for s in self.sun_list:
            pyxel.blt(*s.source)

        for line in range(6):
            # draw plants and zombies
            for plants in self.lines[line]["plants"].values():
                pyxel.blt(*plants.source)
            for zom in self.lines[line]["zombies"]:
                zom.draw()
            # draw bullets
            for bul in self.lines[line]["bullets"]:
                pyxel.blt(*bul.source)
            # draw bomb
            for bomb in self.lines[line]["bomb"]:
                pyxel.blt(*bomb.source)
            # draw cars
            pyxel.blt(self.lines[line]["car"].x, self.lines[line]["car"].y, *self.lines[line]["car"].source)

    def self_producing_sun(self):
        if self.self_pro_sun_counter > 0:
            self.self_pro_sun_counter -= 1
        elif self.self_pro_sun_counter == 0:
            self.sun_list.append(Sun(randint(32, 144), randint(16, 64), randint(64, 96)))
            self.self_pro_sun_counter -= 1
        else:
            self.self_pro_sun_counter = 300

    def mouse_reaction(self):
        # MOUSE REACTION
        x_index = int(pyxel.mouse_x / 16)  # x, y index with respect to the entire canvas
        y_index = int(pyxel.mouse_y / 16)

        # select a plant
        if x_index in range(1, 8) and y_index in range(0, 1) and pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            self.selected_box = [x_index * 16, y_index * 16, 0, 80, 16, 16, 16, 0]  # [x, y, img, u, v, w, h, [colkey]]
            if not (x_index in range(7, 8) and y_index in range(0, 1)) \
                    and self.plants_cd[plant_selection_map[x_index]][1] \
                    and self.sun_num - plant_cost_cd_map[plant_selection_map[x_index]][0] >= 0:
                self.selected_type = plant_selection_map[x_index]
            else:
                self.selected_type = None

        # plant or remove a plant
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) and x_index in range(2, 11) and y_index in range(1, 7):
            if self.selected_type is not None and (x_index - 2) not in self.lines[y_index - 1]["plants"].keys()\
                    and self.sun_num - plant_cost_cd_map[self.selected_type][0] >= 0:
                if self.selected_type == "CherryBomb":
                    self.lines[y_index - 1]["bomb"].append(CherryBomb(x_index * 16, y_index * 16))
                else:
                    self.lines[y_index - 1]["plants"][x_index - 2] = EdiblePlants(self.selected_type,
                                                                                  x_index * 16, y_index * 16)
                self.sun_num -= plant_cost_cd_map[self.selected_type][0]
                self.plants_cd[self.selected_type][0] = plant_cost_cd_map[self.selected_type][1]
                self.plants_cd[self.selected_type][1] = False  # set cd
                self.selected_box = self.selected_type = self.hover_box = None
            else:
                if self.selected_box is not None and self.selected_box[0] == 7 * 16:  # shovel selected
                    try:
                        del self.lines[y_index - 1]["plants"][x_index - 2]
                    except:
                        self.selected_box = None
                        self.hover_box = None
                else:
                    self.selected_box = self.selected_type = self.hover_box = None

        # click outside location to unselect a plant or shovel
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) \
                and not (x_index in range(1, 8) and y_index in range(0, 1)) \
                and not (x_index in range(2, 11) and y_index in range(1, 7)):
            if self.selected_type is not None:
                self.selected_box = self.selected_type = self.hover_box = None
            else:
                if self.selected_box is not None:  # shovel selected
                    self.selected_box = self.hover_box = None

        # mouse and shovel hover prompt
        if not pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON) \
                and x_index in range(2, 11) and y_index in range(1, 7):
            if self.selected_type is not None:  # plants selected
                if (x_index - 2) not in self.lines[y_index - 1]["plants"].keys():
                    self.hover_box = [x_index * 16, y_index * 16, 0, 80, 64, 16, 16, 0]  # green box
                else:
                    self.hover_box = [x_index * 16, y_index * 16, 0, 80, 32, 16, 16, 0]  # red box
            else:
                if self.selected_box is not None and self.selected_box[0] == 7 * 16:  # shovel selected
                    self.hover_box = [x_index * 16, y_index * 16, 0, 80, 48, 16, 16, 4]

    def random_zombies(self, type, times):
        if times <= 0:
            return
        for i in range(times):
            y = choice(list(range(6)))
            self.lines[y]["zombies"].append(
                Zombies(type, zombie_extra_health_map[type], randint(176, 208), (y + 1) * 16)
            )

    def next_wave(self):
        if pyxel.frame_count % 600 == 0 and self.time != 0:  # new wave every 30s
            normal_zombie_num = int(self.time / 30) if self.time <= 450 else 15  # reach max number after 7.5 min
            if self.time != 0 and (self.time == 30 or self.time % 60 == 0):    # just to prevent having too many zombies
                self.random_zombies("FlagZombies", 1)
                self.random_zombies("NormalZombies", normal_zombie_num - 1)
            else:
                self.random_zombies("NormalZombies", normal_zombie_num)
                self.random_zombies("ConeHeadZombies", normal_zombie_num - 1)
                self.random_zombies("NewspaperZombies", normal_zombie_num - 2)
                self.random_zombies("BucketHeadZombies", normal_zombie_num - 3)
                self.random_zombies("ScreenDoorZombies", normal_zombie_num - 4)


if __name__ == "__main__":
    App()
