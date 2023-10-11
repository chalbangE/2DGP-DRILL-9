# 이것은 각 상태들을 객체로 구현한 것임.

from pico2d import *
import math

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE
def time_out(e):
    return e[0] == 'TIME_OUT'
def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT
def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT
def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
class Idle:
    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.dir = 0
        boy.frame = 0
        boy.wait_time = get_time()
        pass
    @staticmethod
    def exit(boy, e):
        pass
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.wait_time > 2:
            boy.state_machine.handle_event(('TIME_OUT', 0))
    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass

class Sleep:
    @staticmethod
    def enter(boy, e):
        boy.frame = 0
    @staticmethod
    def exit(boy, e):
        pass
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
    @staticmethod
    def draw(boy):
        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100,
                        (math.pi * -0.5), 'h', boy.x + 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100,
                        math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100)

class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e):
            boy.dir, boy.action = 1, 1
        elif left_down(e):
            boy.dir, boy.action = -1, 0
        elif right_up(e) or left_up(e):
            boy.dir = 0
    @staticmethod
    def exit(boy, e):
        pass
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        pass
    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)

class AutoRun:
    @staticmethod
    def enter(boy, e):
        if boy.action == 2:
            boy.dir, boy.action = -1, 0
        elif boy.action == 3:
            boy.dir, boy.action = 1, 1

        boy.speed = 3
        boy.frame = 0
        boy.wait_time = get_time()
        boy.size = 200
    @staticmethod
    def exit(boy, e):
        pass
    @staticmethod
    def do(boy):
        if get_time() - boy.wait_time > 4:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        boy.frame = (boy.frame + 1) % 8
        if boy.speed < 10:
            boy.speed += 1
        boy.x += boy.dir * boy.speed

        if boy.x + 50 > 800:
            boy.dir *= -1
            boy.action = 0
        elif boy.x < 0:
            boy.dir *= -1
            boy.action = 1
        pass
    @staticmethod
    def draw(boy):
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100,
                        0, '', boy.x, boy.y + 40, boy.size, boy.size)
class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Sleep
        self.trasitions = {
            Sleep: {space_down: Idle, right_down: Run, left_down: Run, right_up: Idle, left_up: Idle},
            Idle: {time_out: Sleep, right_down: Run, left_down: Run, right_up: Idle, left_up: Idle, a_down: AutoRun},
            Run: {right_down: Run, left_down: Run, right_up: Idle, left_up: Idle, space_down: Idle},
            AutoRun: {time_out: Idle, right_down: Run, left_down: Run, right_up: Idle, left_up: Idle}
        }
    def handle_event(self, e):
        for check_event, next_state in self.trasitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e) # 현 상태를 빼줘야함
                self.cur_state = next_state # trasitions에서 현 상태를 넣었더니 나온 다음 상태를 넣기
                self.cur_state.enter(self.boy, e)
                return True
        return False
    def start(self):
        self.cur_state.enter(self.boy, ('NONE', 0))
    def update(self):
        self.cur_state.do(self.boy)
    def draw(self):
        self.cur_state.draw(self.boy)
class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
