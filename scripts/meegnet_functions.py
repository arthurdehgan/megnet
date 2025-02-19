from meegnet.dataloaders import EpochedDataset, ContinuousDataset
import os
import logging
import numpy as np


def load_info():
    return np.load("../camcan_sensor_locations.npy", allow_pickle=True).tolist()


def load_single_subject(sub, n_samples, args, verbose=2):
    if args.epoched:
        dataset = EpochedDataset(
            sfreq=args.sfreq,
            n_subjects=args.max_subj,
            n_samples=n_samples,
            sensortype=args.sensors,
            lso=args.lso,
            random_state=args.seed,
        )
    else:
        dataset = ContinuousDataset(
            window=args.segment_length,
            overlap=args.overlap,
            sfreq=args.sfreq,
            n_subjects=args.max_subj,
            n_samples=n_samples,
            sensortype=args.sensors,
            lso=args.lso,
            random_state=args.seed,
        )

    dataset.load(args.save_path, one_sub=sub, verbose=verbose)
    return dataset


def prepare_logging(name, args, LOG, fold=None):
    log_name = f"{args.model_name}_{args.seed}_{args.sensors}"
    if fold is not None:
        log_name += f"_fold{args.fold}"
    log_name += f"_{name}.log"
    log_file = os.path.join(args.save_path, log_name)
    logging.basicConfig(filename=log_file, filemode="a")
    LOG.info(f"Starting logging in {log_file}")


def get_input_size(args, default_values):
    if args.feature == "bins":
        trial_length = int(default_values["TRIAL_LENGTH_BINS"])
    elif args.feature == "bands":
        trial_length = int(default_values["TRIAL_LENGTH_BANDS"])
    elif args.feature == "temporal":
        trial_length = int(default_values["TRIAL_LENGTH_TIME"])

    if not args.epoched:
        trial_length = int(args.segment_length * args.sfreq)

    if args.sensors == "MAG":
        n_channels = int(default_values["N_CHANNELS_MAG"])
    elif args.sensors == "GRAD":
        n_channels = int(default_values["N_CHANNELS_GRAD"])
    else:
        n_channels = int(default_values["N_CHANNELS_OTHER"])

    return (
        (1, n_channels, trial_length)
        if args.flat
        else (
            n_channels // int(default_values["N_CHANNELS_MAG"]),
            int(default_values["N_CHANNELS_MAG"]),
            trial_length,
        )
    )


def get_name(args):
    name = f"{args.model_name}_{args.net_option}_{args.seed}_{args.sensors}"
    suffixes = ""
    if args.net_option == "custom_net":
        if args.batchnorm:
            suffixes += "_BN"
        if args.maxpool != 0:
            suffixes += f"_maxpool{args.maxpool}"

        name += f"_dropout{args.dropout}_filter{args.filters}_nchan{args.nchan}_lin{args.linear}_depth{args.hlayers}"
        name += suffixes

    return name
