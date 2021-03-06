import pygame
from creature import Creature
import neat
import os
import sys
import math
from creature import SCALE_ATTR

WIDTH = 1280
HEIGHT = 720

CAPTION = "AI Obstacle Course"
gen = 0

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)

ALLOWED_OBSTACLES = 20
SECONDS_TO_LIVE = 10000
pre = 0
cur_time = 0


def draw_hud(screen, creatures, elapsed_time):
    # generations
    global STAT_FONT, pre, cur_time
    score_label = STAT_FONT.render("Generations: " + str(gen - 1), 1, (255, 255, 255))
    screen.blit(score_label, (10, 10))

    alive_label = STAT_FONT.render("Alive: " + str(len(creatures)), 1, (255, 255, 255))
    screen.blit(alive_label, (10, 50))

    cur_second = int(elapsed_time / 1000)

    if cur_second is not pre:
        cur_time = cur_second
    pre = cur_second

    time_label = STAT_FONT.render("Elapsed time: " + str(cur_time), False, (255, 255, 255))
    screen.blit(time_label, (10, 90))
    return cur_time


def game_start(genomes, config):
    global gen

    elapsed_time = 0
    target_x, target_y = (WIDTH - 350, 100)
    gen += 1
    pygame.init()
    pygame.display.set_caption(CAPTION)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    game_map = pygame.image.load('art/Maze-v2.png').convert()

    game_surf = pygame.Surface((WIDTH, HEIGHT))
    game_surf.fill((200, 255, 0))

    nets = []
    creatures = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        c = Creature(1, WIDTH / 2 - 250, 320, 15)
        creatures.append(c)
        ge.append(genome)

    game_loop = True

    while game_loop and len(creatures) > 0:
        screen.blit(game_map, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        for i, c in enumerate(creatures):
            output = nets[i].activate(c.get_data())
            choice = output.index(max(output))
            c.action_on_input(choice)

            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_RIGHT:
            #         c.action_on_input(0)
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         c.action_on_input(1)
            #

        pygame.draw.circle(screen, (0, 255, 0), (target_x, target_y), 15)

        for c in creatures:
            c.draw(screen, game_map)

        time = draw_hud(screen, creatures, elapsed_time)

        for i, c in enumerate(creatures):
            c.collision = c.check_radar_collision(screen, game_map)

            if c.collision:
                genomes[i][1].fitness -= 30
                nets.pop(creatures.index(c))
                ge.pop(creatures.index(c))
                creatures.pop(creatures.index(c))
            else:
                init_distance = int(math.sqrt((float(c.start_x) - target_x) ** 2 + (c.start_y - target_y) ** 2))
                distance = int(math.sqrt((float(c.x) - target_x) ** 2 + (float(c.y) - target_y) ** 2))
                d_factor: float = (float(init_distance / distance))

                if d_factor < 0:
                    d_factor = 0
                genomes[i][1].fitness += d_factor + (c.speed/(SCALE_ATTR[0]/2))

        if time > 20:
            game_loop = False

        pygame.display.flip()
        dt = clock.tick(60)
        elapsed_time += dt


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(game_start, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.txt')
    run(config_path)
