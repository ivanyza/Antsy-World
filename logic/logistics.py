import multiprocessing as mp
import random as rn

from functools import cache

import misc.ProjSettings as settings
import worldgen

from logic.entities import BaseEntity, SwarmQueen
from world import World
import time

@cache
def get_cords_from_tiled(tiled_area):
    return [(x, y) for x in range(tiled_area[0], tiled_area[2]) for y in
            range(tiled_area[1], tiled_area[3])]


class LogicProcess(mp.Process):
    """
    Backend process that is processing all occurring simulation events.
    """
    def __init__(self, sim_settings, world_settings, manager):
        super(LogicProcess, self).__init__()
        self.name = f"Simulation-{sim_settings.name}"
        self.world_settings = world_settings
        self.sim_settings = sim_settings
        self.tick: int = 0
        self.updates: mp.Queue = mp.Queue()
        self.world = World(self.sim_settings, self.world_settings)
        self.entities: list[BaseEntity] = []
        self.requested = []
        self.manager = manager

    def run(self) -> None:
        self.generator = worldgen.WorldGenHandler(self.world_settings)
        self.generator.start()
        [self.get_rooms([(x, y)]) for x in range(5) for y in range(5)]
        for _ in range(25):
            data = self.generator.output.get()
            # print(data)
            data[1]['entities'] = {}
            self.world.rooms_data[data[0]] = data[1]
        self.entities = []

        for _ in range(100):
            queen = None
            r_cords = rn.choice(list(self.world.rooms_data.keys()))
            while queen is None:
                room = self.world.rooms_data[r_cords]
                cords = rn.choice(list(room['tiles'].keys()))
                if cords in room['tiles'] and room['tiles'][cords]['object'] == 'NormalFloor':
                    queen = SwarmQueen(cords, room, self.world, all_entities=self.entities)
                    self.entities.append(queen)

        counter = 0
        while not self.manager.halted.is_set():
            counter += 1
            self.update()
            if not counter % 10000:
                self.world.save()
        self.generator.halt()
        self.generator.join(timeout=3)
        self.world.save()

    def update(self):
        while not self.generator.output.empty():
            data = self.generator.output.get()
            self.world.rooms_data[data[0]] = data[1]
        [entity.update(self.tick) for entity in self.entities]
        [entity.apply() for entity in self.entities]
        self.entities = list(filter(lambda x: x.alive, self.entities))
        tiled_area = self.manager.get_camera_boundaries()
        cords = get_cords_from_tiled(tiled_area)
        # print(tiles) if tiles != [] else None
        self.manager.set_rooms(self.get_rooms(cords))
        self.tick += 1
        time.sleep(1 / settings.SimSettings.tickrate)

    def get_rooms(self, cords):
        output = {}
        for c in cords:
            if c in self.world.rooms_data:
                output[c] = self.world.rooms_data[c]
            elif c not in self.requested:
                self.requested.append(c)
                self.generator.request(*c)
                self.world.rooms_data[c] = {}
        return output


class GPULogicProcess(mp.Process):
    """
    Backend process that is processing all occurring simulation events.
    """
    def __init__(self, sim_settings, world_settings, manager):
        super(GPULogicProcess, self).__init__()
        self.name = f"Simulation-{sim_settings.name}"
        self.world_settings = world_settings
        self.sim_settings = sim_settings
        self.tick: int = 0
        self.updates: mp.Queue = mp.Queue()
        self.world = World(self.sim_settings, self.world_settings)
        self.entities: list[BaseEntity] = []
        self.requested = []
        self.manager = manager

    def run(self) -> None:
        self.generator = worldgen.WorldGenHandler(self.world_settings)
        self.generator.start()
        [self.get_rooms([(x, y)]) for x in range(5) for y in range(5)]
        for _ in range(25):
            data = self.generator.output.get()
            # print(data)
            data[1]['entities'] = {}
            self.world.rooms_data[data[0]] = data[1]
        self.entities = []

        for _ in range(100):
            queen = None
            r_cords = rn.choice(list(self.world.rooms_data.keys()))
            while queen is None:
                room = self.world.rooms_data[r_cords]
                cords = rn.choice(list(room['tiles'].keys()))
                if cords in room['tiles'] and room['tiles'][cords]['object'] == 'NormalFloor':
                    queen = SwarmQueen(cords, room, self.world, all_entities=self.entities)
                    self.entities.append(queen)

        counter = 0
        while not self.manager.halted.is_set():
            counter += 1
            self.update()
            if not counter % 10000:
                self.world.save()
        self.generator.halt()
        self.generator.join(timeout=3)
        self.world.save()

    def update(self):
        while not self.generator.output.empty():
            data = self.generator.output.get()
            self.world.rooms_data[data[0]] = data[1]
        [entity.update(self.tick) for entity in self.entities]
        [entity.apply() for entity in self.entities]
        self.entities = list(filter(lambda x: x.alive, self.entities))
        tiled_area = self.manager.get_camera_boundaries()
        cords = get_cords_from_tiled(tiled_area)
        # print(tiles) if tiles != [] else None
        self.manager.set_rooms(self.get_rooms(cords))
        self.tick += 1
        time.sleep(1 / settings.SimSettings.tickrate)

    def get_rooms(self, cords):
        output = {}
        for c in cords:
            if c in self.world.rooms_data:
                output[c] = self.world.rooms_data[c]
            elif c not in self.requested:
                self.requested.append(c)
                self.generator.request(*c)
                self.world.rooms_data[c] = {}
        return output
