import argparse
import logging
import time
import torch

from ptlib.dataloaders import FashionDataManager as DataManager
from ptlib.models import SimpleConvNet as Model
from ptlib.trainers import VanillaTrainer as Trainer
from ptlib.utils import get_logging_level
from ptlib.utils import log_function_args


parser = argparse.ArgumentParser()
parser.add_argument('--batch-size', default=32, type=int, help='batch size')
parser.add_argument('--ckpt-path', default='ckpt.tar', type=str,
                    help='checkpoint path')
parser.add_argument('--data-dir', default='', type=str, help='data dir')
parser.add_argument('--log-freq', default=100, type=int,
                    help='logging frequency')
parser.add_argument('--log-level', default='INFO', type=str,
                    help='log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)')
parser.add_argument('--num-epochs', default=100, type=int,
                    help='number of epochs')
parser.add_argument('--short-test', default=False, action='store_true',
                    help='do a short test of the code')
parser.add_argument('--show-progress', default=False, action='store_true',
                    help='print tdqm and other output')


def main(
    batch_size, ckpt_path, data_dir, log_freq, log_level, num_epochs,
    short_test, show_progress
):
    logfilename = 'log_' + __file__.split('/')[-1].split('.')[0] \
        + str(int(time.time())) + '.txt'
    logging.basicConfig(
        filename=logfilename, level=get_logging_level(log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    LOGGER = logging.getLogger(__name__)
    LOGGER.info("Starting...")
    LOGGER.info(__file__)
    log_function_args(vars())

    # set up a data manager and a model
    data_manager = DataManager(data_dir=data_dir)
    model = Model()

    # create a trainer with data handler and model
    trainer = Trainer(data_manager, model, ckpt_path, show_progress)
    trainer.restore_model_and_optimizer()

    # run training
    trainer.train(num_epochs, batch_size, short_test)


if __name__ == '__main__':
    args = parser.parse_args()
    main(**vars(args))
