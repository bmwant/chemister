"""
2-input XOR example -- this is most likely the simplest possible example.
"""
import os
import math
import neat
import visualize

# 2-input XOR inputs and expected outputs.
inputs = [
    (40,1,0,0,0.0,),
    (35,1,0,0,0.0,),
    (42,1,-700,20,0.0),
    (37,1,-700,10,10.0),
    (34,1,-700,0,20.0,),
    (33,1,-1380,20,20.0),
    (39,1,-2040,40,20.0),
    (44,1,-2040,30,30.0),
    (41,1,-2040,20,40.0),
    (45,1,-2040,0,60.0),
]

outputs = [
    (0, 0, 0, 1, 0, 0, 0),
    (0, 1, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 1, 0, 0),
    (0, 0, 0, 0, 1, 0, 0),
    (0, 1, 0, 0, 0, 0, 0),
    (0, 1, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 1, 0, 0),
    (0, 0, 0, 0, 1, 0, 0),
    (0, 0, 0, 0, 0, 1, 0),
    (0, 0, 0, 1, 0, 0, 0),
]


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = 4.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        for xi, xo in zip(inputs, outputs):
            output = net.activate(xi)

            genome.fitness -= (output[0] - xo[0]) ** 2
        genome.fitness = None


def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 300)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    for xi, xo in zip(inputs, outputs):
        output = winner_net.activate(xi)
        print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))

    node_names = {-1:'A', -2: 'B', 0:'A XOR B'}
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)
