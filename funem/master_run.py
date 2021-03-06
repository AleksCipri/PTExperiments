'''
Running modes (`--mode`):

* RUN-TRAINED-HISTORICAL: run a trained policy on historical data.
* RUN-TRAINED-LIVE: run a trained policy on live simulated data.
* TRAIN-HISTORICAL: run a policy with live training from historical data.
* TRAIN-LIVE: run a policy with live training using an asynchronous running
  simulation.

Learners (`--learner`):

* SimpleRuleBased
* SimpleMLP
* SimpleRandom
'''
import argparse
import sys
import logging
import time

import numpy as np

from utils.util_funcs import create_data_source
from utils.util_funcs import create_default_learner_arguments_dict
from utils.util_funcs import create_learner
from utils.util_funcs import create_trainer
from utils.util_funcs import get_logging_level
from utils.common_defs import RUN_MODES
from utils.common_defs import MACHINE_LOG_REFERNECE

import warnings
# 'error' to stop on warns, 'ignore' to ignore silly matplotlib noise
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
parser.add_argument('--ckpt-path', default=None, type=str,
                    help='checkpoint path (full .tar)')
parser.add_argument('--data-source-path',
                    default=MACHINE_LOG_REFERNECE, type=str,
                    help='absolute path for source data')
parser.add_argument('--learner', default='SimpleRuleBased', type=str,
                    help='learner class name')
parser.add_argument('--log-level', default='INFO', type=str,
                    help='log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)')
parser.add_argument('--make-plot', default=False, action='store_true',
                    help='plot win percentages and losses')
parser.add_argument('--mode', default='RUN-TRAINED',
                    type=str, help='run mode')
parser.add_argument('--np-random-seed', default=None, type=int,
                    help='random seed for noise model')
parser.add_argument('--num-epochs', default=1, type=int,
                    help='number of epochs (train)')
parser.add_argument('--num-steps', default=100, type=int,
                    help='number of time steps (train or run)')
parser.add_argument('--show-progress', default=False, action='store_true',
                    help='print tdqm and other output')


def main(
    ckpt_path, data_source_path, learner, log_level, make_plot, mode,
    np_random_seed, num_epochs, num_steps, show_progress
):
    mode = mode.upper()
    if mode not in RUN_MODES:
        print(__doc__)
        sys.exit(1)
    run_time = int(time.time())

    logfilename = 'log_' + __file__.split('/')[-1].split('.')[0] \
        + str(run_time) + '.txt'
    logging.basicConfig(
        filename=logfilename, level=get_logging_level(log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    LOGGER = logging.getLogger(__name__)
    LOGGER.info("Starting...")
    LOGGER.info(__file__)

    if np_random_seed is not None:
        np.random.seed(np_random_seed)

    learner_arguments_dict = create_default_learner_arguments_dict(
        learner, mode
    )
    # # TODO - add code to allow arg dict override...
    if ckpt_path:
        learner_arguments_dict['ckpt_path'] = ckpt_path
    learner_instance = create_learner(learner, learner_arguments_dict)
    data_source = create_data_source(mode, source_path=data_source_path,
                                     maxsteps=num_steps, run_time=run_time)
    trainer = create_trainer(data_source, learner_instance, mode, num_epochs,
                             num_steps, show_progress)
    trainer.restore_model_and_optimizer()
    trainer.train_or_run_model(train=('TRAIN' in mode))
    if make_plot:
        trainer.save_performance_plots()


if __name__ == '__main__':
    args = parser.parse_args()
    main(**vars(args))
